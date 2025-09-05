# Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime
import os

# Load data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, low_memory=False)
        print('Dataset Shape:', df.shape)
        print('\nFirst 5 Rows:\n', df.head(5))
        print('\nColumn Info:\n')
        df.info()
        return df
    except FileNotFoundError:
        print(f'Error: {file_path} not found.')
        return None

# Clean data
def clean_data(df):
    df.columns = df.columns.str.lower().str.strip()
    df = df.fillna({'title 1 length': 0, 'meta description 1 length': 0})
    df['status code'] = pd.to_numeric(df['status code'], errors='coerce')
    df['last modified'] = pd.to_datetime(df['last modified'], errors='coerce')
    html_df = df[df['content type'].str.contains('text/html', na=False)].copy()
    df = df.drop_duplicates(subset=['address'])
    if not os.path.exists('reports'):
        os.makedirs('reports')
    df.to_csv('reports/cleaned_data.csv', index=False)
    print('Data cleaned and saved to reports/cleaned_data.csv')
    return df, html_df

# Analyze crawl overview
def analyze_crawl_overview(df):
    total_urls = len(df)
    print(f'Total URLs: {total_urls}')
    
    status_counts = df['status code'].value_counts()
    plt.figure(figsize=(8, 5))
    status_counts.plot(kind='bar')
    plt.title('Status Code Distribution')
    plt.xlabel('Status Code')
    plt.ylabel('Count')
    plt.savefig('reports/status_codes.png')
    plt.close()
    
    avg_response = df['response time'].mean()
    print(f'Average Response Time: {avg_response:.3f} seconds')
    slow_pages = df[df['response time'] > 0.5][['address', 'response time', 'status code']]
    slow_pages.to_excel('reports/slow_pages.xlsx', index=False)
    print(f'Slow Pages (>0.5s): {len(slow_pages)}')

# Analyze indexability
def analyze_indexability(df):
    non_index = df[df['indexability status'].str.contains('Non-Indexable', na=False)]
    print(f'Non-Indexable Pages: {len(non_index)}')
    non_index[['address', 'indexability status']].to_excel('reports/non_indexable.xlsx', index=False)
    
    missing_canonical = df[df['canonical link element 1'].isna()][['address', 'indexability']]
    print(f'Pages Missing Canonical: {len(missing_canonical)}')
    missing_canonical.to_excel('reports/missing_canonical.xlsx', index=False)
    
    plt.figure(figsize=(8, 5))
    sns.countplot(x='indexability', data=df)
    plt.title('Indexability Status')
    plt.savefig('reports/indexability.png')
    plt.close()

# Analyze on-page SEO
def analyze_onpage_seo(df):
    suboptimal_titles = df[(df['title 1 length'] < 50) | (df['title 1 length'] > 60)]
    print(f'Suboptimal Title Lengths (<50 or >60): {len(suboptimal_titles)}')
    suboptimal_titles[['address', 'title 1', 'title 1 length']].to_excel('reports/suboptimal_titles.xlsx', index=False)
    
    suboptimal_metas = df[(df['meta description 1 length'] < 150) | (df['meta description 1 length'] > 160)]
    print(f'Suboptimal Meta Descriptions (<150 or >160): {len(suboptimal_metas)}')
    suboptimal_metas[['address', 'meta description 1', 'meta description 1 length']].to_excel('reports/suboptimal_metas.xlsx', index=False)
    
    dup_titles = df[df.duplicated(subset=['title 1'], keep=False)].groupby('title 1')['address'].apply(list)
    dup_titles.to_csv('reports/duplicate_titles.csv')
    print(f'Duplicate Titles Found: {len(dup_titles)}')
    
    fig = px.histogram(df, x='title 1 length', title='Title Length Distribution', nbins=50)
    fig.write_html('reports/title_lengths.html')

# Analyze content quality
def analyze_content_quality(df):
    thin_pages = df[df['word count'] < 300][['address', 'word count', 'flesch reading ease score']]
    print(f'Thin Content Pages (<300 words): {len(thin_pages)}')
    thin_pages.to_excel('reports/thin_pages.xlsx', index=False)
    
    low_readability = df[df['flesch reading ease score'] < 60][['address', 'flesch reading ease score']]
    print(f'Low Readability Pages (<60): {len(low_readability)}')
    low_readability.to_excel('reports/low_readability.xlsx', index=False)
    
    near_dups = df[df['no. near duplicates'] > 0][['address', 'closest similarity match']].sort_values('closest similarity match', ascending=False)
    print(f'Near Duplicate Pages: {len(near_dups)}')
    near_dups.to_excel('reports/near_duplicates.xlsx', index=False)
    
    plt.figure(figsize=(8, 5))
    plt.scatter(df['word count'], df['flesch reading ease score'], alpha=0.5)
    plt.xlabel('Word Count')
    plt.ylabel('Flesch Reading Ease Score')
    plt.title('Content Quality: Word Count vs Readability')
    plt.savefig('reports/content_quality.png')
    plt.close()

# Analyze site architecture
def analyze_site_architecture(df):
    deep_pages = df[df['crawl depth'] > 3][['address', 'crawl depth', 'inlinks']]
    print(f'Deep Pages (>3): {len(deep_pages)}')
    deep_pages.to_excel('reports/deep_pages.xlsx', index=False)
    
    low_inlinks = df[df['inlinks'] < 5][['address', 'inlinks', 'link score']].sort_values('link score')
    print(f'Pages with Low Inlinks (<5): {len(low_inlinks)}')
    low_inlinks.to_excel('reports/low_inlinks.xlsx', index=False)
    
    plt.figure(figsize=(10, 6))
    sns.heatmap(df[['crawl depth', 'inlinks', 'outlinks']].corr(), annot=True, cmap='coolwarm')
    plt.title('Correlation: Crawl Depth, Inlinks, Outlinks')
    plt.savefig('reports/link_correlations.png')
    plt.close()

# Analyze performance
def analyze_performance(df):
    large_pages = df[df['size (bytes)'] > 100000][['address', 'size (bytes)', 'content type']]
    print(f'Large Pages (>100KB): {len(large_pages)}')
    large_pages.to_excel('reports/large_pages.xlsx', index=False)
    
    outdated = df[df['last modified'] < datetime.now() - pd.Timedelta(days=365)][['address', 'last modified']]
    print(f'Outdated Pages (>1 year): {len(outdated)}')
    outdated.to_excel('reports/outdated_pages.xlsx', index=False)
    
    old_http = df[df['http version'] == '1.1'][['address', 'http version']]
    print(f'HTTP 1.1 Pages: {len(old_http)}')
    old_http.to_excel('reports/old_http_pages.xlsx', index=False)
    
    plt.figure(figsize=(8, 5))
    sns.boxplot(x='content type', y='size (bytes)', data=df)
    plt.title('Page Size by Content Type')
    plt.xticks(rotation=45)
    plt.savefig('reports/page_size.png')
    plt.close()

# Generate comprehensive report
def generate_report(df, html_df):
    with pd.ExcelWriter('reports/audit_report.xlsx') as writer:
        html_df[['address', 'status code', 'title 1', 'meta description 1', 'word count']].to_excel(writer, sheet_name='HTML Pages', index=False)
        df[df['status code'].between(400, 499)][['address', 'status code']].to_excel(writer, sheet_name='4xx Errors', index=False)
        df[df['response time'] > 0.5][['address', 'response time']].to_excel(writer, sheet_name='Slow Pages', index=False)
        df[df['canonical link element 1'].isna()][['address', 'indexability']].to_excel(writer, sheet_name='Missing Canonical', index=False)
        df[(df['title 1 length'] < 50) | (df['title 1 length'] > 60)][['address', 'title 1', 'title 1 length']].to_excel(writer, sheet_name='Suboptimal Titles', index=False)
        df[(df['meta description 1 length'] < 150) | (df['meta description 1 length'] > 160)][['address', 'meta description 1', 'meta description 1 length']].to_excel(writer, sheet_name='Suboptimal Metas', index=False)
        df[df['word count'] < 300][['address', 'word count']].to_excel(writer, sheet_name='Thin Content', index=False)
        df[df['flesch reading ease score'] < 60][['address', 'flesch reading ease score']].to_excel(writer, sheet_name='Low Readability', index=False)
        df[df['no. near duplicates'] > 0][['address', 'closest similarity match']].to_excel(writer, sheet_name='Near Duplicates', index=False)
        df[df['crawl depth'] > 3][['address', 'crawl depth']].to_excel(writer, sheet_name='Deep Pages', index=False)
        df[df['inlinks'] < 5][['address', 'inlinks', 'link score']].to_excel(writer, sheet_name='Low Inlinks', index=False)
        df[df['size (bytes)'] > 100000][['address', 'size (bytes)']].to_excel(writer, sheet_name='Large Pages', index=False)
        df[df['last modified'] < datetime.now() - pd.Timedelta(days=365)][['address', 'last modified']].to_excel(writer, sheet_name='Outdated Pages', index=False)
        df[df['http version'] == '1.1'][['address', 'http version']].to_excel(writer, sheet_name='HTTP 1.1 Pages', index=False)
    print('SEO Audit Complete. Reports saved to reports/audit_report.xlsx')

# Main execution
if __name__ == "__main__":
    file_path = 'data/raw/internal_all_02.csv'
    df = load_data(file_path)
    if df is None:
        raise SystemExit('Exiting due to file error.')
    df, html_df = clean_data(df)
    analyze_crawl_overview(df)
    analyze_indexability(df)
    analyze_onpage_seo(html_df)
    analyze_content_quality(html_df)
    analyze_site_architecture(df)
    analyze_performance(df)
    generate_report(df, html_df)