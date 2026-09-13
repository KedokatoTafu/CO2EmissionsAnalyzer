from flask import Flask, jsonify, request, Response, render_template
from flask_cors import CORS
import pandas as pd
import io
import sys
from pathlib import Path

try:
    # Fix encoding cho Windows console (Chỉ áp dụng ở local)
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    # Trên Vercel/AWS Lambda, sys.stdout không có hàm reconfigure
    pass

app = Flask(__name__)
app.json.nan_to_null = True  # NaN -> null trong JSON để không lỗi UI
CORS(app)

# ==============================
# 1. Đọc và chuẩn bị dữ liệu
# ==============================
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / 'co2_data_cleaned.csv'

global_error = None
try:
    df = pd.read_csv(CSV_PATH)
    # Loại bỏ hoàn toàn 'World' khỏi dataframe
    df = df[df['country'] != 'World']
    
    # Đảm bảo kiểu dữ liệu cho năm
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    
    # Danh sách các cột dữ liệu phát thải cần xử lý
    emission_cols = [
        'co2', 'coal_co2', 'oil_co2', 'cement_co2', 
        'methane', 'nitrous_oxide', 'total_ghg', 
        'co2_including_luc', 'land_use_change_co2', 'total_ghg_excluding_lucf',
        'population', 'gdp', 'temperature_change_from_co2'
    ]
    
    for col in emission_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
except Exception as e:
    print("LỖI ĐỌC CSV:", e)
    df = pd.DataFrame()
    global_error = f"Lỗi: {str(e)} | Đường dẫn: {CSV_PATH}"

def filter_dataframe(request_args):
    """Hàm hỗ trợ lọc dataframe chung dựa trên params"""
    du_lieu = df.copy()
    
    # Lọc quốc gia
    names_param = request_args.get('countries')
    if names_param:
        name_list = [x.strip() for x in names_param.split(',') if x.strip()]
        if name_list:
            du_lieu = du_lieu[du_lieu['country'].isin(name_list)]
            
    # Lọc thời gian (từ năm - đến năm)
    from_year = request_args.get('from')
    to_year = request_args.get('to')
    if from_year and from_year.isdigit():
        du_lieu = du_lieu[du_lieu['year'] >= int(from_year)]
    if to_year:
        try:
            du_lieu = du_lieu[du_lieu['year'] <= int(to_year)]
        except ValueError:
            pass
        
    # Lọc theo ngưỡng (Sliders) - CHỈ ÁP DỤNG NẾU KHÔNG CHỌN QUỐC GIA CỤ THỂ
    # (Nếu đã cất công click chọn "Afghanistan", thì luôn luôn hiển thị Afghanistan)
    if not request_args.get('countries'):
        min_val = request_args.get('min_val')
        if min_val:
            try:
                source = request_args.get('source', 'co2')
                if source in du_lieu.columns:
                    du_lieu = du_lieu[du_lieu[source] >= float(min_val)]
            except ValueError:
                pass

        min_pop = request_args.get('min_pop')
        if min_pop:
            try:
                du_lieu = du_lieu[du_lieu['population'] >= float(min_pop)]
            except ValueError:
                pass
            
    return du_lieu

# ==============================
# 2. Các Endpoints API
# ==============================
@app.route('/')
def index():
    if global_error:
        import os
        return jsonify({
            "status": "CRASHED",
            "error_message": global_error,
            "cwd": os.getcwd(),
            "files_in_dir": os.listdir(BASE_DIR)
        }), 500
    return render_template('index.html')

@app.route('/api/countries')
def get_countries():
    # Phân loại: Có iso_code là Quốc gia, không có là Khu vực/Châu lục
    # Đồn thời loại bỏ 'World' (Thế giới) khỏi danh sách theo yêu cầu
    df_countries = df[(df['iso_code'].notna()) & (df['country'] != 'World')]
    df_regions = df[(df['iso_code'].isna()) & (df['country'] != 'World')]
    
    countries = sorted(df_countries['country'].unique().tolist())
    regions = sorted(df_regions['country'].unique().tolist())
    
    return jsonify({
        "countries": countries, 
        "regions": regions,
        "min_year": int(df['year'].min()), 
        "max_year": int(df['year'].max())
    })

@app.route('/api/stats')
def get_stats():
    """Lấy số liệu tổng quan (KPIs)"""
    du_lieu = filter_dataframe(request.args)
    if du_lieu.empty:
        return jsonify({"loi": "Không có dữ liệu"}), 404
        
    source = request.args.get('source', 'co2')
    valid_sources = [
        'co2', 'coal_co2', 'oil_co2', 'cement_co2', 
        'methane', 'nitrous_oxide', 'total_ghg', 
        'co2_including_luc', 'land_use_change_co2', 'total_ghg_excluding_lucf'
    ]
    if source not in valid_sources:
        source = 'co2'
        
    agg_func = 'sum'
    
    main_val = du_lieu[source].agg(agg_func)
    
    # Tìm quốc gia và năm cao nhất
    max_idx = du_lieu[source].idxmax()
    if pd.isna(max_idx):
        quoc_gia_max = "--"
        nam_max = "--"
    else:
        quoc_gia_max = du_lieu.loc[max_idx, 'country']
        nam_max = int(du_lieu.loc[max_idx, 'year'])

    return jsonify({
        "main_val": round(main_val, 2),
        "quoc_gia_max": quoc_gia_max,
        "nam_max": nam_max,
        "so_quoc_gia": du_lieu['country'].nunique()
    })

@app.route('/api/chart/map')
def chart_map():
    du_lieu = df.copy()
    
    source = request.args.get('source', 'co2')
    valid_sources = [
        'co2', 'coal_co2', 'oil_co2', 'cement_co2', 
        'methane', 'nitrous_oxide', 'total_ghg', 
        'co2_including_luc', 'land_use_change_co2', 'total_ghg_excluding_lucf'
    ]
    if source not in valid_sources:
        source = 'co2'
        
    agg_func = 'sum'

    from_year = request.args.get('from')
    to_year = request.args.get('to')
    if from_year and from_year.isdigit():
        du_lieu = du_lieu[du_lieu['year'] >= int(from_year)]
    if to_year and to_year.isdigit():
        du_lieu = du_lieu[du_lieu['year'] <= int(to_year)]
        
    du_lieu = du_lieu[du_lieu['iso_code'].notna()]
    
    map_data = du_lieu.groupby(['iso_code', 'country'])[source].agg(agg_func).reset_index()
    
    return jsonify({
        "iso_codes": map_data['iso_code'].tolist(),
        "countries": map_data['country'].tolist(),
        "co2": map_data[source].round(2).tolist()
    })

@app.route('/api/chart/line')
def chart_line():
    du_lieu = filter_dataframe(request.args).copy()
    if du_lieu.empty:
        return jsonify({"loi": "Không có dữ liệu"}), 404

    source = request.args.get('source', 'co2')
    valid_sources = [
        'co2', 'coal_co2', 'oil_co2', 'cement_co2', 
        'methane', 'nitrous_oxide', 'total_ghg', 
        'co2_including_luc', 'land_use_change_co2', 'total_ghg_excluding_lucf'
    ]
    if source not in valid_sources:
        source = 'co2'
        
    agg_func = 'sum'

    top_countries = du_lieu.groupby('country')[source].agg(agg_func).sort_values(ascending=False).head(10).index.tolist()
    du_lieu['country_grouped'] = du_lieu['country'].apply(lambda x: x if x in top_countries else 'Các quốc gia khác')
    pivot = du_lieu.pivot_table(index='year', columns='country_grouped', values=source, aggfunc=agg_func).fillna(0)
    
    col_totals = pivot.sum().sort_values(ascending=False)
    cols = [c for c in col_totals.index if c != 'Các quốc gia khác']
    if 'Các quốc gia khác' in pivot.columns:
        cols.append('Các quốc gia khác')

    datasets = []
    for country in cols:
        datasets.append({
            "label": country,
            "data": pivot[country].tolist()
        })
        
    return jsonify({
        "labels": pivot.index.tolist(),
        "datasets": datasets
    })

@app.route('/api/chart/pie')
def chart_pie():
    du_lieu = filter_dataframe(request.args)
    if du_lieu.empty:
        return jsonify({"loi": "Không có dữ liệu"}), 404

    source = request.args.get('source', 'co2')
    valid_sources = [
        'co2', 'coal_co2', 'oil_co2', 'cement_co2', 
        'methane', 'nitrous_oxide', 'total_ghg', 
        'co2_including_luc', 'land_use_change_co2', 'total_ghg_excluding_lucf'
    ]
    if source not in valid_sources:
        source = 'co2'
        
    agg_func = 'sum'
    
    # Nhóm theo quốc gia và lấy Top 5
    country_totals = du_lieu.groupby('country')[source].agg(agg_func).sort_values(ascending=False)
    top5 = country_totals.head(5)
    others = country_totals.iloc[5:].sum() if len(country_totals) > 5 else 0
    
    labels = top5.index.tolist()
    data = top5.round(2).tolist()
    
    if others > 0:
        labels.append("Khác")
        data.append(round(others, 2))
        
    return jsonify({
        "labels": labels,
        "data": data
    })

@app.route('/api/chart/bar')
def chart_bar():
    du_lieu = filter_dataframe(request.args)
    if du_lieu.empty:
        return jsonify({"loi": "Không có dữ liệu"}), 404

    source = request.args.get('source', 'co2')
    valid_sources = [
        'co2', 'coal_co2', 'oil_co2', 'cement_co2', 
        'methane', 'nitrous_oxide', 'total_ghg', 
        'co2_including_luc', 'land_use_change_co2', 'total_ghg_excluding_lucf'
    ]
    if source not in valid_sources:
        source = 'co2'
        
    agg_func = 'sum'

    ket_qua = du_lieu.groupby('country')[source].agg(agg_func).sort_values(ascending=False).head(15)
    
    return jsonify({
        "labels": ket_qua.index.tolist(),
        "data": ket_qua.round(2).tolist()
    })

@app.route('/api/chart/sparklines')
def chart_sparklines():
    """Dữ liệu cho 4 biểu đồ mini (Yếu tố tác động) ở dưới cùng"""
    du_lieu = filter_dataframe(request.args)
    if du_lieu.empty:
        return jsonify({})
        
    trend = du_lieu.groupby('year').agg({
        'land_use_change_co2': 'sum',
        'temperature_change_from_co2': 'sum',
        'population': 'sum',
        'gdp': 'sum'
    }).fillna(0)
    
    return jsonify({
        'labels': trend.index.tolist(),
        'land_use': trend['land_use_change_co2'].tolist(),
        'temperature': trend['temperature_change_from_co2'].tolist(),
        'population': trend['population'].tolist(),
        'gdp': trend['gdp'].tolist()
    })

@app.route('/api/simulation_data')
def simulation_data():
    """Dữ liệu tổng quan để mô phỏng (Có lọc theo quốc gia/năm)"""
    du_lieu = filter_dataframe(request.args)
    if du_lieu.empty:
        return jsonify({})

    trend = du_lieu.groupby('year').agg({
        'coal_co2': 'sum',
        'oil_co2': 'sum',
        'cement_co2': 'sum',
        'methane': 'sum',
        'land_use_change_co2': 'sum',
        'temperature_change_from_co2': 'sum',
        'population': 'sum',
        'gdp': 'sum'
    }).fillna(0)
    
    return jsonify({
        'labels': trend.index.tolist(),
        'coal': trend['coal_co2'].tolist(),
        'oil': trend['oil_co2'].tolist(),
        'cement': trend['cement_co2'].tolist(),
        'methane': trend['methane'].tolist(),
        'land_use': trend['land_use_change_co2'].tolist(),
        'temperature': trend['temperature_change_from_co2'].tolist(),
        'population': trend['population'].tolist(),
        'gdp': trend['gdp'].tolist()
    })

@app.route('/api/download-csv')
def download_csv():
    """Xuất file CSV theo bộ lọc"""
    du_lieu = filter_dataframe(request.args)
    if du_lieu.empty:
        return "Không có dữ liệu", 404

    output = io.StringIO()
    du_lieu.to_csv(output, index=False)
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=co2_export.csv"}
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
