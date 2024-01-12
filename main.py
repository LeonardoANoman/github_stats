import requests
import pandas as pd
import os
import matplotlib.pyplot as plt

def get_repos_stats():
    token = ""
    USERNAME = ""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.github.com/users/{USERNAME}/repos"
    request = requests.get(url, headers=headers)
    if request.status_code == 200:
        response = request.json()
    else:
        raise Exception(f"Query failed to run by returning code of {request.status_code}")
    language_data_list = []

    for repo in response:
        languages_url = repo["languages_url"]
        print(languages_url)
        languages_request = requests.get(languages_url, headers=headers)

        if languages_request.status_code == 200:
            languages_data = languages_request.json()
            repo_size = sum(languages_data.values())
            language_data_list.append({"Size": repo_size, **languages_data})
        else:
            print(f"Failed to fetch languages for repository {repo['name']}. Status Code: {languages_request.status_code}")

    df = pd.DataFrame(language_data_list)
    
    directory_name = 'csv'  
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    else:
        print(f"Directory {directory_name} already exists.")
    df.to_csv("csv/data.csv", index=False)
    
def filter_python():
    # Drops .ipynb :( (need a solution for this)

    df = pd.read_csv("csv/data.csv")
    column_to_drop = "Jupyter Notebook"
    if column_to_drop in df.columns:
        df = df.drop(columns=[column_to_drop])
    else:
        print(f"Column '{column_to_drop}' not found in the DataFrame.")
    df.to_csv("csv/stats.csv", index=False)

def sum_languages():
    df = pd.read_csv("csv/stats.csv") 
    sum_df = df.sum(axis=0).reset_index()
    sum_df.columns = ["Language", "Sum"]
    sum_df.to_csv("csv/final.csv", index=False)

def generate_chart_raw():
    df = pd.read_csv("csv/final.csv")
    df = df.drop(index=0)
    df = df.sort_values(by="Sum",ascending=False)

    df['Percentage'] = (df['Sum'] / df['Sum'].sum()) * 100

    colors = plt.cm.tab10.colors

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(aspect="equal"))

    wedges, texts, autotexts = ax.pie(df['Sum'], labels=df['Language'], autopct='',
                                textprops=dict(color="w"), colors=colors, wedgeprops=dict(width=0.5),
                                pctdistance=0.8)

    
    centre_circle = plt.Circle((0, 0), 0.6, color='white', fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    ax.set_title("Languages used on my GitHub", fontsize=16)

    legend_languages = ax.legend(wedges, df["Language"],
                            title="Languages",
                            loc="center left",
                            bbox_to_anchor=(1.1, 0, 0, 1))

    legend_percentages = ax.legend(wedges, df["Percentage"].round(2).astype(str) + '%',
                            title="Percentage",
                            loc="center right",
                            bbox_to_anchor=(1.1, 0, 0, 1))

    ax.add_artist(legend_languages)
    ax.add_artist(legend_percentages)

    plt.show()

if __name__ == "__main__":
    get_repos_stats()
    filter_python()
    sum_languages()
    generate_chart_raw()