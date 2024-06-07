import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from parse import parse
import sys
from optparse import OptionParser
from scipy import interpolate
from scipy.interpolate import CubicSpline
import re
import os
import matplotlib
matplotlib.use('agg')


class optParser():  
    def __init__(self, fakeArgs):
        parser = OptionParser()
        parser.add_option('-f', '--free_ene_csv', dest='free_ene_csv', help='The name of the free energy csv file to be analyzed')
        parser.add_option('-b', '--bar_ene_csv', dest='bar_ene_csv', help='The name of the BAR free energy csv file', default='BARfree_ene.csv')
        parser.add_option('-l', '--lambda_col_name', dest='lambda_col_name', help='The name of the column that record lambda.', default='delta_A_what_to_what')
        parser.add_option('-e', '--fe_col_name', dest='fe_col_name', help='The name of the column that record free energy.', default='free_energy(kcal/mol)')
        parser.add_option('-p', '--png_file', dest='png_file', help='The name of the output png file.', default='dG_dlambda.png')
        parser.add_option('-m', '--fe_mode', dest='fe_mode', help='The mode of the free energy csv file. BAR or FEP', default='BAR')
        parser.add_option('-w', '--cal_wins', dest='cal_wins', help='The filename that give the windows information for calculation. If you give the string of "all", the program will not filter any data.', default='all')

        if fakeArgs:
            self.option, self.args = parser.parse_args(fakeArgs)
        else:
            self.option, self.args = parser.parse_args()

class CSpline():
    def __init__(self, df, cal_lst):
        self.df = df
        # self.df['dlambda'] = self.df[fe_col_name]/self.df['dG_dlambda']
        self.cal_lst = cal_lst
        if self.cal_lst != 'all':
            print(f'cal_win_lst:{self.cal_lst}')
            self.df = self.extract_part(self.df, self.cal_lst)
    
    def extract_part(self, df, cal_lst):
        for i in range(len(cal_lst)):
            cal_lst[i] = str(cal_lst[i])
        df = df.loc[self.df['lambda_value'].isin(cal_lst)]
        return df

        '''
尝试使用B spline, 默认选项设置下为3次样条，拟合情况和cubic spline一样。暂时弃用。 
    # def plot_dG_dlamda_bspline(self, png_file=None):
    #     if self.cal_lst != 'all':
    #         print(f'cal_win_lst:{self.cal_lst}')
    #         df = self.extract_part(self.df, self.cal_lst)
    #     else:
    #         df = self.df
    #     df_crg = df[df['lambda_labels']=='charge']
    #     df_vdw = df[df['lambda_labels']=='vdw']
    #     pattern = '({},{},{})'
    #     for index in df_crg.index:
    #         crg_lambda_value = parse(pattern, df_crg['lambda_value'][index])
    #         df_crg.loc[index,'lambda_value'] = crg_lambda_value[1]
    #     for index in df_vdw.index:
    #         vdw_lambda_value = parse(pattern, df_vdw['lambda_value'][index])
    #         df_vdw.loc[index,'lambda_value'] = vdw_lambda_value[2]
    #     df_crg['lambda_value'] = df_crg['lambda_value'].astype(float)
    #     df_vdw['lambda_value'] = df_vdw['lambda_value'].astype(float)
    #     # print('cspline',df_crg,'\n',df_vdw)
    #     if png_file is not None:
    #         png_crg = 'Bpline-charge_'+png_file
    #         png_vdw = 'Bpline-vdw_'+png_file
    #     else:
    #         png_crg, png_vdw = None, None
    #     inte_crg = self.plotting_bspline(df_crg, png_crg, True)
    #     inte_vdw = self.plotting_bspline(df_vdw, png_vdw, False)
    #     return inte_crg, inte_vdw

    # def plotting_bspline(self, df, png_file=None, ifcrg=True):
    #     # x = np.array(df['lambda_value']+df['dlambda']/2)
    #     x = np.array(df['lambda_value'])
    #     y = np.array(df['dG_dlambda'])
    #     if ifcrg:
    #         pass
    #     else:
    #         x = np.append(x,1.0)
    #         y = np.append(y,y[-1])
    #     x2 = np.linspace(0,1,100)
    #     tck = interpolate.splrep(x, y)
    #     y_bspline = interpolate.splev(x2, tck)

    #     plt.plot(x, y, 'o', color='black', markersize=4, label='data')
    #     plt.plot(x2, y_bspline, color='black', markersize=3, label='b_spline')
    #     plt.legend()
    #     # 设置坐标轴标签
    #     plt.xticks(x, x, rotation=90)
    #     plt.ylabel(r'$\delta G_{cal}/\delta \lambda $ (kcal/mol)', )#y轴标签
    #     plt.xlabel(r'$\lambda$ info',)#x轴标签
    #     # plt.minorticks_on()#开启小坐标
    #     plt.tick_params(which='major',width=3, length=6)#设置大刻度的大小
    #     # plt.tick_params(which='minor',width=2, length=4)#设置小刻度的大小
    #     ax=plt.gca();#获得坐标轴的句柄
    #     ax.spines['bottom'].set_linewidth(4);#设置底部坐标轴的粗细
    #     ax.spines['left'].set_linewidth(4);#设置左边坐标轴的粗细
    #     ax.spines['right'].set_linewidth(4);#设置右边坐标轴的粗细
    #     ax.spines['top'].set_linewidth(4);#设置上部坐标轴的粗细
    #     plt.tight_layout()
    #     # 显示图形
    #     if png_file is not None:
    #         plt.savefig(png_file,dpi=600)
    #     else:
    #         plt.show()
    #     plt.clf()
    #     inte = interpolate.splint(0,1,tck)
    #     # dG_sum = self.data_obj.dG_sum
    #     return inte
        '''

    def cubic(self, x, y):
        ## x is a 1-D array of lambda values, and should be in strictly increasing order.
        ## y can have arbitrary number of dimensions, but every axis should have the same length with x.
        # cs_obj = CubicSpline(x, y, bc_type='natural')
        cs_obj = CubicSpline(x, y)
        return cs_obj
    
    def plot_dG_dlamda_spline(self, df, png_file=None):
        print(f'__________df:\n{df}')
        df_crg = df[df['lambda_labels']=='charge']
        df_vdw = df[df['lambda_labels']=='vdw']
        # pattern = '({},{},{})'
        # for index in df_crg.index:
        #     crg_lambda_value = parse(pattern, df_crg['lambda_value'][index])
        #     df_crg.loc[index,'lambda_value'] = crg_lambda_value[1]
        # for index in df_vdw.index:
        #     vdw_lambda_value = parse(pattern, df_vdw['lambda_value'][index])
        #     df_vdw.loc[index,'lambda_value'] = vdw_lambda_value[2]
        # df_crg['lambda_value'] = df_crg['lambda_value'].astype(float)
        # df_vdw['lambda_value'] = df_vdw['lambda_value'].astype(float)
        # print('cspline',df_crg,'\n',df_vdw)
        if png_file is not None:
            png_crg = 'CSpline-charge_'+png_file
            png_vdw = 'CSpline-vdw_'+png_file
        else:
            png_crg, png_vdw = None, None
        inte_crg = self.plotting_cubic(df_crg, png_crg)
        inte_vdw = self.plotting_cubic(df_vdw, png_vdw)
        return inte_crg, inte_vdw
    
    def plotting_cubic(self, df, png_file=None):
        df = df.drop_duplicates(['lambda_info'])
        x = np.array(df['lambda_info'])
        y = np.array(df['dG_dlambda'])
        # if x[-1] == x[-2]:
        #     x = np.delete(x,-1)
        #     y = np.delete(y,-1)
        x2 = np.linspace(0,1,100)
        cs_obj = self.cubic(x, y)

        plt.plot(x, y, 'o', color='black', markersize=4, label='data')
        plt.plot(x2, cs_obj(x2), color='black', markersize=3, label='cubic_spline')
        plt.legend()
        # 设置坐标轴标签
        plt.xticks(x, df['delta_A_what_to_what'], rotation=90)
        plt.ylabel(r'$\delta G_{cal}/\delta \lambda $ (kcal/mol)', )#y轴标签
        plt.xlabel(r'$\lambda$ info',)#x轴标签
        # plt.minorticks_on()#开启小坐标
        plt.tick_params(which='major',width=3, length=6)#设置大刻度的大小
        # plt.tick_params(which='minor',width=2, length=4)#设置小刻度的大小
        ax=plt.gca();#获得坐标轴的句柄
        ax.spines['bottom'].set_linewidth(4);#设置底部坐标轴的粗细
        ax.spines['left'].set_linewidth(4);#设置左边坐标轴的粗细
        ax.spines['right'].set_linewidth(4);#设置右边坐标轴的粗细
        ax.spines['top'].set_linewidth(4);#设置上部坐标轴的粗细
        plt.tight_layout()
        # 显示图形
        if png_file is not None:
            plt.savefig(png_file,dpi=600)
        else:
            plt.show()
        plt.clf()
        inte = cs_obj.integrate(0,1)
        # dG_sum = self.data_obj.dG_sum
        return inte

class dG_dlambda(ABC):
    def __init__(self, csv_file, fe_mode='BAR'):
        self.csv_file = csv_file
        self.df_csv = pd.read_csv(self.csv_file, delimiter="|")
        # self.df_csv = pd.read_csv(self.csv_file)
        # if fe_mode == 'FEP':
        #     self.reset_index()

    def reset_index(self):
        self.df_csv.rename(columns={'FEP_forward_bythislambda(kcal/mol)':fe_col_name}, inplace=True)
        # self.df_csv.rename(columns={'lambda_value':lambda_col_name}, inplace=True)
        # print(self.df_csv)
        new_index = []
        for i in range(self.df_csv.shape[0]-1):
            index_cur = self.df_csv['lambda_value'][i]
            index_nex = self.df_csv['lambda_value'][i+1]
            new_index.append(f'{index_cur} to {index_nex}')
        self.df_csv.dropna(axis=0, how='any', inplace=True)
        self.df_csv[lambda_col_name] = new_index
        # self.df_csv = self.df_csv.rename_axis('delta_A_what_to_what').reset_index()
        # print(self.df_csv)    

    @abstractmethod
    def parse_lambda(self, lambda_col_value):
        '''
        Customlize your parse_lambda
        
        '''
        pass
    
    def get_dG_dlambda(self, lambda_col_name, free_ene_col_name):
        dG_dlambda_values = []
        labels = []
        lambda_infos = []
        for index, row in self.df_csv.iterrows():
            lambda_col_value = row[lambda_col_name]
            free_ene_col_value = row[free_ene_col_name]
            dlambda, label, lambda_info_x = self.parse_lambda(lambda_col_value)
            dG_dlambda = free_ene_col_value/dlambda
            dG_dlambda_values.append(dG_dlambda)
            labels.append(label)
            lambda_infos.append(lambda_info_x)
        self.df_csv = self.df_csv.assign(dG_dlambda=dG_dlambda_values)
        self.df_csv = self.df_csv.assign(lambda_labels=labels)
        self.df_csv = self.df_csv.assign(lambda_info=lambda_infos)
        # print(self.df_csv)

    def plot_dG_dlambda(self, png_file=None):
        df = self.df_csv.drop(self.df_csv[self.df_csv['lambda_labels']=='mix'].index)
        df_crg = df[df['lambda_labels']=='charge']
        df_vdw = df[df['lambda_labels']=='vdw']
        
        # print(df_)
        df_crg.to_csv(fe_mode+'_charge.csv', index=None)
        df_vdw.to_csv(fe_mode+'_vdw.csv', index=None)
        if png_file is not None:
            png_crg = 'charge'+png_file
            png_vdw = 'vdw'+png_file
        else:
            png_crg, png_vdw = None, None
        if not df_crg.empty:
            self.plotting(df_crg, png_crg)
        if not df_vdw.empty:
            self.plotting(df_vdw, png_vdw)

    def plotting(self, df, png_file=None):
        # 设置柱状图的颜色
        color_dict = {
            'restraint': 'tab:red',
            'charge': 'tab:blue',
            'vdw': 'tab:green'
        }
        # plt.figure(figsize=(10,10))
        # 绘制柱状图
        plt.bar(df.index, df['dG_dlambda'], color=[color_dict[l] for l in df['lambda_labels']])
        # 绘制直线
        plt.plot(df.index, df['dG_dlambda'], color='black')
        # 设置x轴标签
        plt.xticks(df.index, df['delta_A_what_to_what'], rotation=90)
        plt.ylabel(r'$\delta G_{cal}/\delta \lambda $ (kcal/mol)', )#y轴标签
        plt.xlabel(r'$\lambda$ info',)#x轴标签
        
        # plt.minorticks_on()#开启小坐标
        plt.tick_params(which='major',width=3, length=6)#设置大刻度的大小
        # plt.tick_params(which='minor',width=2, length=4)#设置小刻度的大小
        ax=plt.gca();#获得坐标轴的句柄
        ax.spines['bottom'].set_linewidth(4);#设置底部坐标轴的粗细
        ax.spines['left'].set_linewidth(4);#设置左边坐标轴的粗细
        ax.spines['right'].set_linewidth(4);#设置右边坐标轴的粗细
        ax.spines['top'].set_linewidth(4);#设置上部坐标轴的粗细
        plt.tight_layout()
        # 显示图形
        if png_file is not None:
            plt.savefig(png_file, format="png",dpi=600, transparent=True)
        else:
            plt.show()
        plt.clf()

class ABFE_dG_dlambda(dG_dlambda):
    def __init__(self, csv_file, fe_mode):
        super().__init__(csv_file, fe_mode)

    def parse_lambda(self, lambda_col_value):
        '''
        parse the lambda string like: '(0.0, 0.0, 0.0) to (1.0, 0.0, 0.0)'
        '''
        pattern = '({},{},{}) to ({},{},{})'
        result = parse(pattern, lambda_col_value)
        start_coords = np.array([float(result[0]), float(result[1]), float(result[2])])
        end_coords = np.array([float(result[3]), float(result[4]), float(result[5])])
        dd_coords = start_coords-end_coords
        nonzero_count = np.count_nonzero(dd_coords)
        labels = ['restraint', 'charge', 'vdw']
        if nonzero_count == 1:
            dlambda = np.linalg.norm(dd_coords)
            nonzero_indices = np.argwhere(dd_coords != 0).flatten()
            # 根据位置确定标签
            if len(nonzero_indices) == 1:
                if nonzero_indices[0] < len(labels):
                    label = labels[nonzero_indices[0]]
                    lambda_info_x = (start_coords[nonzero_indices[0]]+end_coords[nonzero_indices[0]])/2
                else:
                    label = 'unknown'
                    lambda_info_x = None
            else:
                label = 'unknown'
                lambda_info_x = None
        else:
            print('Warning you change more than one lambda simultaneously')
            print(lambda_col_value)
            label = 'mix'
            lambda_info_x = None
            nonzero_elements = dd_coords[dd_coords != 0]
            result = np.all(nonzero_elements == nonzero_elements[0])
            if result:
                dlambda = nonzero_elements[0]
            else:
                print('The changed lambdas are not equal, dlambda will be None')
                dlambda= None
        return dlambda, label, lambda_info_x

if __name__ == '__main__':
    opts = optParser('') 
    free_ene_csv = opts.option.free_ene_csv
    bar_ene_csv = opts.option.bar_ene_csv
    lambda_col_name = opts.option.lambda_col_name
    fe_col_name = opts.option.fe_col_name
    png_file = opts.option.png_file
    fe_mode = str(opts.option.fe_mode)
    ts = ABFE_dG_dlambda(free_ene_csv, fe_mode)
    ts.df_csv = ts.df_csv[:-1] # drop the last row
    ts.get_dG_dlambda(lambda_col_name, fe_col_name)
    ts.plot_dG_dlambda(png_file)

    # print(ts.df_csv)
    if 'restraint' in ts.df_csv['lambda_labels'].values:
        dG_restraint = float(ts.df_csv[fe_col_name][ts.df_csv[ts.df_csv['lambda_labels']=='restraint'].index[0]])
    else:
        dG_restraint = 0
    
    # pre_ene_tot = ts.df_csv[fe_col_name].sum()
    if os.path.exists(bar_ene_csv):
        bar_df = pd.read_csv(bar_ene_csv, delimiter="|")
        print(bar_df)
        pre_ene_tot = bar_df.iloc[-1,1]
    else:
        pre_ene_tot = ts.df_csv[fe_col_name].sum()

    if fe_mode == 'FEP':
        df_result = pd.DataFrame()
        if opts.option.cal_wins == 'all':
            cal_win_lst = 'all'
            ts_cs = CSpline(ts.df_csv, cal_win_lst)
            inte_crg, inte_vdw = ts_cs.plot_dG_dlamda_spline(ts_cs.df, png_file)
            single_df = pd.DataFrame(data=[['all', dG_restraint, inte_crg, inte_vdw, dG_restraint+inte_crg+inte_vdw, pre_ene_tot]])
            df_result = pd.concat([df_result, single_df], axis=0)
        else:
            with open(opts.option.cal_wins, 'r') as f:
                f_content = f.readlines()
                cal_win_lst = [eval(line.strip()) for line in f_content]
                import sys 
                if not isinstance(cal_win_lst, list):
                    print('Error: The content of the win_lst file is not a list!')
                    sys.exit()
                print(len(cal_win_lst))
            ts_cs = CSpline(ts.df_csv, 'all')
            inte_crg, inte_vdw = ts_cs.plot_dG_dlamda_spline(ts_cs.df, 'all_'+png_file)
            # inte_crg, inte_vdw = ts_cs.plot_dG_dlamda_bspline('all_'+png_file)
            single_df = pd.DataFrame(data=[['all', dG_restraint, inte_crg, inte_vdw, dG_restraint+inte_crg+inte_vdw, pre_ene_tot]])
            df_result = pd.concat([df_result, single_df], axis=0)
            for idx_ in range(0, len(cal_win_lst)):
                win_lst = cal_win_lst[idx_]
                ts_cs = CSpline(ts.df_csv, win_lst)
                inte_crg, inte_vdw = ts_cs.plot_dG_dlamda_spline(ts_cs.df, str(idx_)+'_'+png_file)
                # inte_crg, inte_vdw = ts_cs.plot_dG_dlamda_bspline(str(idx_)+'_'+png_file)
                single_df = pd.DataFrame(data=[[idx_, dG_restraint, inte_crg, inte_vdw, dG_restraint+inte_crg+inte_vdw, pre_ene_tot]])
                df_result = pd.concat([df_result, single_df], axis=0)
        df_result.to_csv('cubic_spline_result.csv', index=None, header=None)
