import plotly .express as px 
import plotly .graph_objects as go 
import pandas as pd 

def plot_revenue_vs_expenses (df :pd .DataFrame ):
    fig =px .line (df ,x ='date',y =['revenue','expenses'],
    title ='Revenue vs Expenses Trend',
    labels ={'value':'Amount ($)','variable':'Metric'})
    fig .update_layout (template ='plotly_dark',hovermode ='x unified')
    return fig 

def plot_profit_trend (df :pd .DataFrame ):
    if 'profit'not in df .columns :
        df ['profit']=df ['revenue']-df ['expenses']
    fig =px .area (df ,x ='date',y ='profit',title ='Net Profit Trend',
    color_discrete_sequence =['#00CC96'])
    fig .update_layout (template ='plotly_dark')
    return fig 

def plot_health_gauge (score :float ):
    fig =go .Figure (go .Indicator (
    mode ="gauge+number",
    value =score ,
    title ={'text':"Business Health Score"},
    gauge ={
    'axis':{'range':[0 ,100 ]},
    'bar':{'color':"#00d4ff"},
    'steps':[
    {'range':[0 ,40 ],'color':"red"},
    {'range':[40 ,70 ],'color':"orange"},
    {'range':[70 ,100 ],'color':"green"}],
    }
    ))
    fig .update_layout (template ='plotly_dark',height =300 )
    return fig 

def plot_forecast (df :pd .DataFrame ,forecast_df :pd .DataFrame ,metric :str ):
    fig =go .Figure ()
    fig .add_trace (go .Scatter (x =df ['date'],y =df [metric ],name ='Historical',line =dict (color ='#00d4ff')))
    fig .add_trace (go .Scatter (x =forecast_df ['date'],y =forecast_df ['realistic'],name ='Forecast',line =dict (dash ='dash')))
    fig .add_trace (go .Scatter (x =forecast_df ['date'],y =forecast_df ['best_case'],fill =None ,mode ='lines',line_color ='rgba(0,255,0,0.2)',name ='Best Case'))
    fig .add_trace (go .Scatter (x =forecast_df ['date'],y =forecast_df ['worst_case'],fill ='tonexty',mode ='lines',line_color ='rgba(255,0,0,0.2)',name ='Worst Case'))

    if metric in ['revenue','profit']:
        fig .update_yaxes (rangemode ="tozero")

    fig .update_layout (title =f'{metric .capitalize ()} Forecast',template ='plotly_dark')
    return fig 
