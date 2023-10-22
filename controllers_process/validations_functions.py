import streamlit as st
from formatterInputs import *
from control.matlab import tf, c2d, tfdata
from connections import *
from session_state import get_session_variable
from controllers_process.performace_metrics import *
from numpy import convolve,array

def coefficients_validations(coeff_string):
    if  coeff_string == '':
        return None
    if not validateFloatInput(coeff_string):
        return st.error('''Insira valores decimais separados por vírgula.     
                        ex:  0.9 , 0.134''')

def plot_chart_validation(plot_variable,y:str,height= 200, x = 'Time (s)'):
    if plot_variable is None:
        return None
    if plot_variable.empty:
        return None
    
    return st.line_chart(data= plot_variable,x = x, y = y,height=height)

def convert_tf_2_discrete(num_coeff:str,den_coeff:str,tf_type:str,f_gpc_mimo_checkbox:bool, K_alpha:float|None  = 0, alpha_fgpc:float|None = 0):
    
    sampling_time = get_session_variable('sampling_time')
    num_coeff_float = string2floatArray(num_coeff)
    den_coeff_float = string2floatArray(den_coeff)
    

    if tf_type == 'Discreto':
        Gm1 = tf(num_coeff_float, den_coeff_float,sampling_time)   
    
    # Motor 1 Model Transfer Function
    Gm1 = tf(num_coeff_float, den_coeff_float)
    Gmz1 = c2d(Gm1, sampling_time)
    num1, den1 = tfdata(Gmz1)
    Am1 = den1[0][0]
    Bm1 = num1[0][0]
    
    if f_gpc_mimo_checkbox:
        alpha_filter = K_alpha*array([1,-alpha_fgpc])
        Bm1 = convolve(Bm1,alpha_filter)

    
    return Am1, Bm1

def validateFloatInput(input_numbers_str:str):
    if ',' in input_numbers_str:
        parts = input_numbers_str.split(',')
    
        for part in parts:
            part = part.strip()
            try:
                float(part)
            except ValueError:
                return False
        
        return True
    
    else:
        try:
            float(input_numbers_str)
        except ValueError:
            return False
        return True


def string2floatArray(input_numbers_str:str) -> list[float] | float:
    '''
    Split the input string into an array of numbers
    '''
    if ',' in input_numbers_str:
        return [float(num.strip()) for num in input_numbers_str.split(',')]
    else:
        return float(input_numbers_str)
    


def iae_metric_validation():
    if not get_session_variable('reference_input'):
        return None
    if not get_session_variable('process_output_sensor'):
        return None
    
    previous_iae_metric = get_session_variable('iae_metric')
    iae_metric = integrated_absolute_error()
    delta_iae = iae_metric-previous_iae_metric
    st.session_state.controller_parameters['iae_metric'] = iae_metric

    return st.metric('Integrated Absolute Error', f'{iae_metric:.2f}',delta=f'{delta_iae:.3f}')
    

def tvc1_validation():
    if not get_session_variable('control_signal_1'):
        return None
    
    previous_tvc1= get_session_variable('tvc_1_metric')
    total_variation_control_1 = total_variation_control('control_signal_1')
    delta_tvc1 = total_variation_control_1-previous_tvc1
    st.session_state.controller_parameters['tvc_1_metric'] = total_variation_control_1
     
    if not get_session_variable('control_signal_2'):
        return st.metric('Total Variation Control 1', f'{total_variation_control_1:.2f}',delta=f'{delta_tvc1:.3f}')
    previous_tvc2= get_session_variable('tvc_2_metric')
    total_variation_control_2 = total_variation_control('control_signal_2')
    delta_tvc2 = total_variation_control_2-previous_tvc2
    st.session_state.controller_parameters['tvc_2_metric'] = total_variation_control_1
    
    return st.metric('Total Variation Control 1', f'{total_variation_control_1:.2f}',delta=f'{delta_tvc1:.3f}'), \
           st.metric('Total Variation Control 2', f'{total_variation_control_2:.2f}',delta=f'{delta_tvc2:.3f}')