import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_test_excel():
    """创建测试用的Excel文件"""
    
    # 生成销售数据
    np.random.seed(42)
    
    # 日期范围
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(365)]
    
    # 产品类别
    categories = ['电子产品', '服装', '食品', '书籍', '家具']
    
    # 生成数据
    data = []
    for i, date in enumerate(dates):
        # 每天随机生成3-8条销售记录
        daily_records = np.random.randint(3, 9)
        
        for _ in range(daily_records):
            category = np.random.choice(categories)
            
            # 根据类别设置不同的价格范围
            if category == '电子产品':
                price = np.random.normal(800, 300)
            elif category == '服装':
                price = np.random.normal(200, 80)
            elif category == '食品':
                price = np.random.normal(50, 20)
            elif category == '书籍':
                price = np.random.normal(80, 30)
            else:  # 家具
                price = np.random.normal(1200, 500)
            
            price = max(10, price)  # 确保价格为正
            
            # 数量
            quantity = np.random.randint(1, 6)
            
            # 总金额
            total = price * quantity
            
            # 地区
            region = np.random.choice(['北京', '上海', '广州', '深圳', '杭州'])
            
            # 客户年龄
            age = np.random.randint(18, 66)
            
            data.append({
                '日期': date.strftime('%Y-%m-%d'),
                '产品类别': category,
                '单价': round(price, 2),
                '数量': quantity,
                '总金额': round(total, 2),
                '地区': region,
                '客户年龄': age
            })
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 保存为Excel
    df.to_excel('test_sales_data.xlsx', index=False)
    print(f"✅ 已生成测试数据文件: test_sales_data.xlsx")
    print(f"📊 数据概览:")
    print(f"   - 总记录数: {len(df):,}")
    print(f"   - 日期范围: {df['日期'].min()} 到 {df['日期'].max()}")
    print(f"   - 产品类别: {', '.join(df['产品类别'].unique())}")
    print(f"   - 地区: {', '.join(df['地区'].unique())}")
    print(f"   - 总销售额: ¥{df['总金额'].sum():,.2f}")
    
    return df

if __name__ == "__main__":
    create_test_excel()