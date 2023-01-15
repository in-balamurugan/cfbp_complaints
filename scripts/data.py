from datetime import date, timedelta
import plotly.graph_objs as go
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import requests
#from transformers import pipeline
from collections import Counter



def return_figures():
    #'company': 'GOLDMAN SACHS BANK USA',
    payload = {'company': 'GOLDMAN SACHS BANK USA', 'product': 'Credit card or prepaid card', 'size': '10000',
               'company_received_min': '2019-06-30'}
    r = requests.get('https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?',
                     params=payload)

    a = r.json()
    l = a['hits']['hits']
    df = pd.json_normalize(l)

    selector_d = {'_source.product': 'product', '_source.complaint_what_happened': 'cause', '_source.issue': 'issue',
                  '_source.sub_product': 'sub_product', '_source.has_narrative': 'has_narrative',
                  '_source.company_response': 'response',
                  '_source.company': 'company', '_source.date_received': 'date',
                  '_source.company_public_response': 'public_response',
                  '_source.sub_issue': 'sub_issue'}
    df = df.rename(columns=selector_d)[selector_d.values()]

    df_gs = df
    df_gs['date'] = pd.to_datetime(df['date']).dt.date
    df_gs['month_year'] = pd.to_datetime(df_gs['date'], errors='coerce', format='%Y-%m-%d').astype("datetime64[M]")

    df_gs_top_issues_count = df_gs.groupby(['issue']).size().reset_index(name='counts').sort_values('counts',
                                                                                                    ascending=False).head(
        1)
    issue_list = ['Problem with a purchase shown on your statement','Incorrect information on your report','Problem with a credit reporting company\'s investigation into an existing problem','Problem with fraud alerts or security freezes','Unexpected or other fees']
    df_gs_issue_count = df_gs.groupby(['issue', 'month_year']).size().reset_index(name='counts')
    df_gs_issue_count = df_gs_issue_count[df_gs_issue_count['issue'].isin(issue_list)]


    graph_one = []


    for issue in issue_list:
        x_val = df_gs_issue_count[df_gs_issue_count['issue'] == issue].month_year.tolist()
        y_val = df_gs_issue_count[df_gs_issue_count['issue'] == issue].counts.tolist()
        graph_one.append(
            go.Scatter(
                x=x_val,
                y= y_val,
                mode="lines",
                name = issue,

            )

    )

    layout_one = dict(title='Issues',showlegend=False
                      )

    sub_issue_list = \
    df_gs.groupby(['sub_issue']).size().reset_index(name='counts').sort_values('counts', ascending=False).head(15)[
        'sub_issue'].to_list()
    df_gs_sub_issue_count = df_gs.groupby(['issue', 'sub_issue']).size().reset_index(name='counts')
    df_gs_sub_issue_count = df_gs_sub_issue_count[df_gs_sub_issue_count['sub_issue'].isin(sub_issue_list)]

    graph_two = []
    graph_two.append(
        go.Treemap(
            parents=[""] * len(df_gs_sub_issue_count['sub_issue']),
            labels=df_gs_sub_issue_count['sub_issue'],
            values=df_gs_sub_issue_count['counts'],
            textinfo="label+value",

        )
    )

    layout_two = dict(title='Issues raised', name = "Issue 2",
                      )



    # payload = {'size': '10000', 'company':'GOLDMAN SACHS BANK USA'}

    payload = {'product': 'Credit card or prepaid card', 'size': '10000',
               'company_received_min': (date.today() - timedelta(days=90)).isoformat()}
    r = requests.get('https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?',
                     params=payload)

    a = r.json()
    l = a['hits']['hits']
    df = pd.json_normalize(l)
    selector_d = {'_source.product': 'product', '_source.complaint_what_happened': 'cause', '_source.issue': 'issue',
                  '_source.sub_product': 'sub_product', '_source.has_narrative': 'has_narrative',
                  '_source.company_response': 'response',
                  '_source.company': 'company', '_source.date_received': 'date',
                  '_source.company_public_response': 'public_response',
                  '_source.sub_issue': 'sub_issue'}
    df = df.rename(columns=selector_d)[selector_d.values()]
    df['company_category'] = np.where(df.company == 'GOLDMAN SACHS BANK USA', 'GSBU_', 'Rest_')

    df_title = df.groupby(['company_category', 'issue'], as_index=False).size()
    df_title = df_title.pivot(index='issue', columns='company_category', values='size')
    df_title['Rest'] = df_title['Rest_'] / df_title['Rest_'].sum() * 100
    df_title['GSBU'] = df_title['GSBU_'] / df_title['GSBU_'].sum() * 100

    df_title.sort_values(by=['GSBU'], ascending=False, inplace=True)
    df_title.reset_index(inplace=True)

    print(df_title)
    graph_three = []
    graph_three.append(
        go.Bar(
            x=df_title['issue'],
            y=df_title['GSBU'],
        )
    )

    graph_three.append(
        go.Bar(
            x=df_title['issue'],
            y=df_title['Rest'],
        )
    )

    layout_three = dict(title='Issues raised', name = "Issue 2",
                      )

    # complaint_text = list(filter(lambda x: x != '', df['cause']))
    #
    # classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base",
    #                       return_all_scores=False)
    # result = []
    # for x in complaint_text:
    #     score = classifier(x, truncation=True)
    #     result.append(score[0]['label'])
    #
    # count_emotion = Counter(result)
    # labels = list(count_emotion.keys())
    # values = list(count_emotion.values())
    #
    # graph_four = []
    # graph_four.append(
    #     go.Pie(
    #         labels=labels, values=values
    # )
    # )
    #
    # layout_four = dict(title='Issues raised', name = "Issue 2",
    #                   )








    # append all charts
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    #figures.append(dict(data=graph_four, layout=layout_four))
    return figures