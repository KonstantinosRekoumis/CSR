"""
This module provides the functions that calculate the pressures applied on the plates.\n
This is done only for Strength Assessment! Not Fatigue Assessment!
"""
import math
from modules.utilities import c_error, c_success,c_warn,lin_int_dict,d2r
import modules.classes as cls
from modules.constants import RHO_F,RHO_S,G

class PhysicsData:
    '''
    -------------------------------------------------------------------------------------------------------------------
    PhysicsData: Class that holds each different simulation scenario data to pass to the appropriate
    pressure evaluation functions.
    For the Proper Scenario parameters go to pages 181-182\n
    For the kr_p and GM_p parameters use the percentages of tables 1,2 in pages 181-182 they default for Full Load Homogeneous Loading\n
    fbk needs more
    -------------------------------------------------------------------------------------------------------------------
    '''
    def __init__(self,Tlc:float,ship:cls.ship,cond:str,rho = RHO_S, kr_p = .35,GM_p=0.12, fbk = 1.2):
        # Ship Data and General Data
        self.cond = cond #The dynamic condition we are interested in
        self.int_cond = self.cond+'_DLP'
        self.Tlc = Tlc
        self.rho = rho
        self.LBP =  ship.LBP
        self.B  = ship.B 
        self.Cw = ship.Cw
        self.Lsc =  ship.Lsc
        self.Cb = ship.Cb
        self.D = ship.D
        self.a0 = ship.a0
        self.Iyy = ship.Iyy        
        self.Ixx = ship.Ixx
        self.yn = ship.yo
        self.xn = ship.xo
        # Universal Coefficients
        self.fxL = 0.5 # As the middle section is the object of study
        self.fps = 1.0 # Extreme Loads Scenario pp. 180 (to fill the other cases)
        if self.Tlc <= ship.Tsc: #pp. 180
            self.ft = self.Tlc/ship.Tsc
        else :
            c_error("Your current Draught must not exceed the Scantling Draught.\n The program Terminates....")
            quit()
        if self.ft <= 0.5: self.ft = 0.5
        self.fbeta = {
            'HSM-1' :1.05,'HSM-2' :1.05,
            'HSA-1' :1.00,'HSA-2' :1.00,
            'FSM-1' :1.05,'FSM-2' :1.05,
            'BSR-1P':0.80,'BSR-2P':0.80,
            'BSP-1P':0.80,'BSP-2P':0.80,
            'OST-1P':1.00,'OST-2P':1.00,
            'OSA-1P':1.00,'OSA-2P':1.00,
        } # pp. 186 Part 1 Chapter 4 Section 4
        try:
            self.fb = self.fbeta[self.cond] 
        except KeyError:
            c_error(f'PhysicsData/__init__(): {self.cond} is not a valid Dynamic Condition abbreviation.')
            c_error("Invalid condition to study. Enter an appropriate Condition out of :",default=False)
            [c_error(f"{i}",default=False) for i in self.fbeta]
            c_error('Currently supported conditions are : HSM and BSP.\n The other conditions will result in invalid results',default=False)
            c_error('The Program Terminates...',default=False)
            quit()

        self.flp = 1.0 if (self.fxL >= 0.5) else -1.0

        #roll angle
        self.T_theta = (2.3*math.pi*kr_p*self.B)/math.sqrt(G*GM_p*self.B)
        self.theta   = (9000*(1.25-0.025*self.T_theta)*self.fps*fbk)/((self.B + 75)*math.pi) # deg 
        #pitch angle
        self.T_phi = math.sqrt((math.pi*1.2*(1+self.ft)*self.Lsc)/G)
        self.phi   = 1350*self.fps*self.Lsc**(-0.94)*(1.0+(2.57/math.sqrt(G*self.Lsc))**1.2) # deg  
        # Acceleration at the center of Gravity [m/s^2]
        self.a_surge = 0.2*self.fps*self.a0*G
        self.a_sway  = 0.3*self.fps*self.a0*G
        self.a_heave =     self.fps*self.a0*G
        self.a_pitch = self.fps*((3.1/math.sqrt(G*self.Lsc))+1)*self.phi*math.pi/180*(2*math.pi/self.T_phi)**2
        self.a_roll  = self.fps*self.theta*math.pi/180*(2*math.pi/self.T_theta)**2


        self.flp_osa_d = {'< 0.4':-(0.2+0.3*self.ft),'[0.4,0.6]':(-(0.2+0.3*self.ft))*(5.6-11.5*self.fxL) ,'> 0.6': 1.3*(0.2+0.3*self.ft)}
        self.flp_ost_d = {'< 0.2':5*self.fxL,'[0.2,0.4]':1.0,'[0.4,0.65]':-7.6*self.fxL+4.04,'[0.65,0.85]':-0.9,'> 0.85':6*(self.fxL-1)}

        #as fxl = 0.5
        
        self.flp_osa = self.flp_osa_d['[0.4,0.6]'] 
        self.flp_ost = self.flp_ost_d['[0.4,0.65]']

        self.wave_pressure = 0
        self.wave_pressure_functions()

        self.Cwv,self.Cqw,self.Cwh,self.Cwt,self.Cxs,self.Cxp,self.Cxg,self.Cys,self.Cyr,self.Cyg,self.Czh,self.Czr,self.Czg = self.Combination_Factors()
        # Bending Moments and Shear Forces calculation
        self.Mwv_lc,self.Qwv_lc,self.Mwh_lc,self.Mws = self.moments_eval() #maybe later add torsional calculations
        self.sigma = lambda y,z: 1e-3*((self.Mwv_lc+self.Mws)/self.Ixx*(z-self.yn)-self.Mwh_lc/self.Iyy*y)

    def debug(self,what2print:str):
        print('condition :',self.cond)
        if 'angles' in what2print:
            print(f'theta:{self.theta}')
            print(f'phi:{self.phi}')
        if 'accels' in what2print:
            print('a0:',self.a0)
            print('a_surge : ',self.a_surge)
            print('a_sway  : ',self.a_sway )
            print('a_heave : ',self.a_heave)
            print('a_pitch : ',self.a_pitch)
            print('a_roll  : ',self.a_roll )
        if 'particulars' in  what2print:
            print('Tlc : ',self.Tlc)
            print('rho : ',self.rho)
            print('LBP : ',self.LBP)
            print('B : ',self.B)
            print('Cw : ',self.Cw)
            print('Lsc : ',self.Lsc)
            print('D : ',self.D)

    def external_loadsC(self):
        '''
        -------------------------------------------------------------------------------------------------------------------
        Function that returns data for the constants that need to be passed to the external forces calculating functions.
        Output:\n
            A tuple containing:
            fxL, fps, fb, ft,\n
            rho -> <float> Target water's density (default : sea water @ 17 Celsius)\n
            LBP, B, Cw, Lsc,\n
            Tlc ->  <float> Loading Condition Draught, Depth\n

        ---------+----------------------------------------------------------------------------------------------------------
        '''
        return self.fxL, self.fps, self.fb, self.ft,self.rho,self.LBP, self.B, self.Cw,self.Lsc,self.Tlc, self.D

    def Combination_Factors(self):

        # C = ['Cwv','Cqw','Cwh','Cwt','Cxs','Cxp','Cxg','Cys','Cyr','Cyg','Czh','Czr','Czp']
        HSM_1   =[-1  ,-self.fps,     0,0,0.3-0.2*self.ft, -0.7, 0.6, 0, 0, 0, 0.5*self.ft-0.15, 0, 0.7]
        HSA_1   =[-0.7,-0.6*self.flp,0,0,0.2,-0.4*(self.ft+1),0.4*(self.ft+1),0,0,0,0.4*self.ft-0.1,0,-0.4*(self.ft+1)]
        FSM_1   =[-0.4*self.ft-0.6,-self.fps,0,0,0.2-0.4*self.ft,0.15,-0.2,0,0,0,0,0,0.15]
        BSR_1P  =[0.1 -0.2*self.ft,(0.1-0.2*self.ft)*self.flp,1.2*1.1*self.ft,0,0,0,0,0.2-0.2*self.ft,1,-1,0.7-0.4*self.ft,1,0]
        BSP_1P  =[0.3 -0.8*self.ft,(0.3-0.8*self.ft)*self.flp,0.7-0.7*self.ft,0,0,0.1-0.3*self.ft,0.3*self.ft-0.1,-0.9,0.3,-0.2,1,0.3,0.1-0.3*self.ft]
        OSA_1P  =[0.75-0.5*self.ft,(0.6-0.4*self.ft)*self.flp,.55+0.2*self.ft,-self.flp_osa,0.1*self.ft-0.45,1,-1,-0.2-0.1*self.ft,0.3-0.2*self.ft,0.1*self.ft-0.2,-0.2*self.ft,0.3-0.2*self.ft,1]
        OST_1P  =[-0.3-0.2*self.ft,(-.35-.2*self.ft)*self.flp,-.9,-self.flp_ost,0.1*self.ft-0.15,0.7-0.3*self.ft,0.2*self.ft-0.45,0,0.4*self.ft-0.25,0.1-0.2*self.ft,0.2*self.ft-0.05,0.4*self.ft-0.25,0.7-0.3*self.ft] 
        
        
        Cwv = {'HSM-1': HSM_1[ 0] ,'HSM-2': -1*HSM_1[ 0],'HSA-1': HSA_1[ 0] ,'HSA-2': -1*HSA_1[ 0] ,'FSM-1': FSM_1[ 0] ,'FSM-2': -1*FSM_1[ 0] ,'BSR-1P': BSR_1P[ 0] ,'BSR-2P': -1*BSR_1P[ 0] ,'BSP-1P': BSP_1P[ 0],'BSP-2P': -1*BSP_1P[ 0],'OST-1P': OST_1P[ 0],'OST-2P': -1*OST_1P[ 0],'OSA-1P': OSA_1P[ 0] ,'OSA-2P': -1*OSA_1P[ 0] }
        Cqw = {'HSM-1': HSM_1[ 1] ,'HSM-2': -1*HSM_1[ 1],'HSA-1': HSA_1[ 1] ,'HSA-2': -1*HSA_1[ 1] ,'FSM-1': FSM_1[ 1] ,'FSM-2': -1*FSM_1[ 1] ,'BSR-1P': BSR_1P[ 1] ,'BSR-2P': -1*BSR_1P[ 1] ,'BSP-1P': BSP_1P[ 1],'BSP-2P': -1*BSP_1P[ 1],'OST-1P': OST_1P[ 1],'OST-2P': -1*OST_1P[ 1],'OSA-1P': OSA_1P[ 1] ,'OSA-2P': -1*OSA_1P[ 1] }
        Cwh = {'HSM-1': HSM_1[ 2] ,'HSM-2': -1*HSM_1[ 2],'HSA-1': HSA_1[ 2] ,'HSA-2': -1*HSA_1[ 2] ,'FSM-1': FSM_1[ 2] ,'FSM-2': -1*FSM_1[ 2] ,'BSR-1P': BSR_1P[ 2] ,'BSR-2P': -1*BSR_1P[ 2] ,'BSP-1P': BSP_1P[ 2],'BSP-2P': -1*BSP_1P[ 2],'OST-1P': OST_1P[ 2],'OST-2P': -1*OST_1P[ 2],'OSA-1P': OSA_1P[ 2] ,'OSA-2P': -1*OSA_1P[ 2] }
        Cwt = {'HSM-1': HSM_1[ 3] ,'HSM-2': -1*HSM_1[ 3],'HSA-1': HSA_1[ 3] ,'HSA-2': -1*HSA_1[ 3] ,'FSM-1': FSM_1[ 3] ,'FSM-2': -1*FSM_1[ 3] ,'BSR-1P': BSR_1P[ 3] ,'BSR-2P': -1*BSR_1P[ 3] ,'BSP-1P': BSP_1P[ 3],'BSP-2P': -1*BSP_1P[ 3],'OST-1P': OST_1P[ 3],'OST-2P': -1*OST_1P[ 3],'OSA-1P': OSA_1P[ 3] ,'OSA-2P': -1*OSA_1P[ 3] }
        Cxs = {'HSM-1': HSM_1[ 4] ,'HSM-2': -1*HSM_1[ 4],'HSA-1': HSA_1[ 4] ,'HSA-2': -1*HSA_1[ 4] ,'FSM-1': FSM_1[ 4] ,'FSM-2': -1*FSM_1[ 4] ,'BSR-1P': BSR_1P[ 4] ,'BSR-2P': -1*BSR_1P[ 4] ,'BSP-1P': BSP_1P[ 4],'BSP-2P': -1*BSP_1P[ 4],'OST-1P': OST_1P[ 4],'OST-2P': -1*OST_1P[ 4],'OSA-1P': OSA_1P[ 4] ,'OSA-2P': -1*OSA_1P[ 4] }
        Cxp = {'HSM-1': HSM_1[ 5] ,'HSM-2': -1*HSM_1[ 5],'HSA-1': HSA_1[ 5] ,'HSA-2': -1*HSA_1[ 5] ,'FSM-1': FSM_1[ 5] ,'FSM-2': -1*FSM_1[ 5] ,'BSR-1P': BSR_1P[ 5] ,'BSR-2P': -1*BSR_1P[ 5] ,'BSP-1P': BSP_1P[ 5],'BSP-2P': -1*BSP_1P[ 5],'OST-1P': OST_1P[ 5],'OST-2P': -1*OST_1P[ 5],'OSA-1P': OSA_1P[ 5] ,'OSA-2P': -1*OSA_1P[ 5] }
        Cxg = {'HSM-1': HSM_1[ 6] ,'HSM-2': -1*HSM_1[ 6],'HSA-1': HSA_1[ 6] ,'HSA-2': -1*HSA_1[ 6] ,'FSM-1': FSM_1[ 6] ,'FSM-2': -1*FSM_1[ 6] ,'BSR-1P': BSR_1P[ 6] ,'BSR-2P': -1*BSR_1P[ 6] ,'BSP-1P': BSP_1P[ 6],'BSP-2P': -1*BSP_1P[ 6],'OST-1P': OST_1P[ 6],'OST-2P': -1*OST_1P[ 6],'OSA-1P': OSA_1P[ 6] ,'OSA-2P': -1*OSA_1P[ 6] }
        Cys = {'HSM-1': HSM_1[ 7] ,'HSM-2': -1*HSM_1[ 7],'HSA-1': HSA_1[ 7] ,'HSA-2': -1*HSA_1[ 7] ,'FSM-1': FSM_1[ 7] ,'FSM-2': -1*FSM_1[ 7] ,'BSR-1P': BSR_1P[ 7] ,'BSR-2P': -1*BSR_1P[ 7] ,'BSP-1P': BSP_1P[ 7],'BSP-2P': -1*BSP_1P[ 7],'OST-1P': OST_1P[ 7],'OST-2P': -1*OST_1P[ 7],'OSA-1P': OSA_1P[ 7] ,'OSA-2P': -1*OSA_1P[ 7] }
        Cyr = {'HSM-1': HSM_1[ 8] ,'HSM-2': -1*HSM_1[ 8],'HSA-1': HSA_1[ 8] ,'HSA-2': -1*HSA_1[ 8] ,'FSM-1': FSM_1[ 8] ,'FSM-2': -1*FSM_1[ 8] ,'BSR-1P': BSR_1P[ 8] ,'BSR-2P': -1*BSR_1P[ 8] ,'BSP-1P': BSP_1P[ 8],'BSP-2P': -1*BSP_1P[ 8],'OST-1P': OST_1P[ 8],'OST-2P': -1*OST_1P[ 8],'OSA-1P': OSA_1P[ 8] ,'OSA-2P': -1*OSA_1P[ 8] }
        Cyg = {'HSM-1': HSM_1[ 9] ,'HSM-2': -1*HSM_1[ 9],'HSA-1': HSA_1[ 9] ,'HSA-2': -1*HSA_1[ 9] ,'FSM-1': FSM_1[ 9] ,'FSM-2': -1*FSM_1[ 9] ,'BSR-1P': BSR_1P[ 9] ,'BSR-2P': -1*BSR_1P[ 9] ,'BSP-1P': BSP_1P[ 9],'BSP-2P': -1*BSP_1P[ 9],'OST-1P': OST_1P[ 9],'OST-2P': -1*OST_1P[ 9],'OSA-1P': OSA_1P[ 9] ,'OSA-2P': -1*OSA_1P[ 9] }
        Czh = {'HSM-1': HSM_1[10] ,'HSM-2': -1*HSM_1[10],'HSA-1': HSA_1[10] ,'HSA-2': -1*HSA_1[10] ,'FSM-1': FSM_1[10] ,'FSM-2': -1*FSM_1[10] ,'BSR-1P': BSR_1P[10] ,'BSR-2P': -1*BSR_1P[10] ,'BSP-1P': BSP_1P[10],'BSP-2P': -1*BSP_1P[10],'OST-1P': OST_1P[10],'OST-2P': -1*OST_1P[10],'OSA-1P': OSA_1P[10] ,'OSA-2P': -1*OSA_1P[10] }
        Czr = {'HSM-1': HSM_1[11] ,'HSM-2': -1*HSM_1[11],'HSA-1': HSA_1[11] ,'HSA-2': -1*HSA_1[11] ,'FSM-1': FSM_1[11] ,'FSM-2': -1*FSM_1[11] ,'BSR-1P': BSR_1P[11] ,'BSR-2P': -1*BSR_1P[11] ,'BSP-1P': BSP_1P[11],'BSP-2P': -1*BSP_1P[11],'OST-1P': OST_1P[11],'OST-2P': -1*OST_1P[11],'OSA-1P': OSA_1P[11] ,'OSA-2P': -1*OSA_1P[11] }
        Czg = {'HSM-1': HSM_1[12] ,'HSM-2': -1*HSM_1[12],'HSA-1': HSA_1[12] ,'HSA-2': -1*HSA_1[12] ,'FSM-1': FSM_1[12] ,'FSM-2': -1*FSM_1[12] ,'BSR-1P': BSR_1P[12] ,'BSR-2P': -1*BSR_1P[12] ,'BSP-1P': BSP_1P[12],'BSP-2P': -1*BSP_1P[12],'OST-1P': OST_1P[12],'OST-2P': -1*OST_1P[12],'OSA-1P': OSA_1P[12] ,'OSA-2P': -1*OSA_1P[12] }

        try:
            return Cwv[self.cond],Cqw[self.cond],Cwh[self.cond],Cwt[self.cond],Cxs[self.cond],Cxp[self.cond],Cxg[self.cond],Cys[self.cond],Cyr[self.cond],Cyg[self.cond],Czh[self.cond],Czr[self.cond],Czg[self.cond]
        except KeyError:
            c_error(f'PhysicsData/Combination_Factors: {self.cond} is not a valid Dynamic Condition abbreviation.')
            c_error("Invalid condition to study. Enter an appropriate Condition out of :",default=False)
            [c_error(f"{i}",default=False) for i in fbeta]
            c_error('Currently supported conditions are : HSM and BSP.\n The other conditions will result in invalid results',default=False)
            c_error('The Program Terminates...',default=False)
            quit()

    def accel_eval(self,point,debug=False):
        R =  min((self.D/4+self.Tlc/2,self.D/2))
        x,y,z = point
        if debug:
            print('Point [x,y,z] : ',point)
            print('Cxs',self.Cxs,' Cxp',self.Cxp,' Cxg',self.Cxg,' Cys',self.Cys,' Cyr',self.Cyr,' Cyg',self.Cyg,' Czh',self.Czh,' Czr',self.Czr,' Czg',self.Czg)
        ax = -self.Cxg*G*math.sin(d2r(self.phi))+self.Cxs*self.a_surge+self.Cxp*self.a_pitch*(z-R)
        ay = self.Cyg*G*math.sin(d2r(self.theta))+self.Cys*self.a_sway-self.Cyr*self.a_roll*(z-R)
        az = self.Czh*self.a_heave+self.Czr*self.a_roll*y-self.Czg*self.a_pitch*(x-0.45*self.Lsc)

        return ax,ay,az
    
    def wave_pressure_functions(self):
        functions = {
            'HSM': HSM_wave_pressure,
            'BSP': BSP_wave_pressure
        }

        try:
            if ('-1P' in self.cond) or ('-2P' in self.cond):self.wave_pressure = functions[self.cond[:-3]]
            else:self.wave_pressure = functions[self.cond[:-2]]
        except KeyError:
            c_error(f'(physics.py) PhysicsData/wave_pressure_functions: \'{self.cond[:-2]}\' is not yet supported. Program terminates to avoid unpredictable behavior...')
            quit()
    
    def moments_eval(self):
        fnl_h = 1.0 # strength assessment Hogging
        fnl_s = 0.58*(self.Cb+0.7)/self.Cb # strength assessment Sagging
        fm_  = {
            0.0 : 0.0,
            0.4 : 1.0,
            0.6 : 1.0,
            1.0 : 0.0
        }
        fqpos_ = {
            0.0 : 0.0,
            0.2 : 0.92*fnl_h,
            0.3 : 0.92*fnl_h,
            0.4 : 0.7,
            0.6 : 0.7,
            0.7 : 1.0*fnl_s,
            0.85: 1.0*fnl_s,
            1.0 : 0.0 
        }
        fqneg_ = {
            0.0 : 0.0,
            0.2 : 0.92*fnl_s,
            0.3 : 0.92*fnl_s,
            0.4 : 0.7,
            0.6 : 0.7,
            0.7 : 1.0*fnl_h,
            0.85: 1.0*fnl_h,
            1.0 : 0.0 
        }
        fsw_ ={
            0.0 : 0.0,
            0.1 : 0.15,
            0.3 : 1.0,
            0.7 : 1.0,
            0.9 : 0.15,
            1.0 : 0.0             
        }


        # Vertical Moment Calculation
        Mw_h = lambda x :  0.19*fnl_h*x*self.fps*self.Cw*self.Lsc**2*self.B*self.Cb
        Mw_s = lambda x : -0.19*fnl_s*x*self.fps*self.Cw*self.Lsc**2*self.B*self.Cb
        # Shear Forces Calculation
        Qpos = lambda x :  0.52*x*self.fps*self.Cw*self.Lsc*self.B*self.Cb
        Qneg = lambda x : -0.52*x*self.fps*self.Cw*self.Lsc*self.B*self.Cb
        
        fm = lin_int_dict(fm_,self.fxL)
        fm_mid = lin_int_dict(fm_,0.5)
        fqpos = lin_int_dict(fqpos_,self.fxL)
        fqneg = lin_int_dict(fqneg_,self.fxL)
        fsw = lin_int_dict(fsw_,self.fxL)

        if self.Cwv >= 0:
            Mwv_lc = self.fb*self.Cwv*Mw_h(fm)
            Mws = fsw*((0.171*self.Cw*self.Lsc**2*self.B*(self.Cb+0.7))-Mw_h(fm_mid))
        else:
            Mwv_lc = self.fb*self.Cwv*abs(Mw_s(fm))
            Mws = -0.85*fsw*((0.171*self.Cw*self.Lsc**2*self.B*(self.Cb+0.7))+Mw_s(fm_mid))

        if self.Cqw >= 0:
            Qwv_lc = self.fb*self.Cqw*Qpos(fqpos)
        else:
            Qwv_lc = self.fb*self.Cqw*abs(Qneg(fqneg))
        # Horizontal Moment Calculation
        Mwh = 0.9*self.fps*fm*(0.31+self.Lsc/2800)*self.Cw*self.Lsc**2*self.Tlc*self.Cb

        

        return Mwv_lc,Qwv_lc,self.Cwh*Mwh, Mws


#---- Pressure Calculating Functions -----

def hydrostatic_pressure(z:float,Zmax:float,rho:float):
    '''
    Convention is that the zero is located at the keel plate
    '''
    if 0<=z :
        dT = Zmax - z  
        return rho*G*dT
    # elif 0<z and z>Zmax:
    #     return 0
    else:
        c_warn(f"physics.hydrostatic_pressure : Your input was invalid. The function returns by default 0\n \
            your input was ({z},{Zmax},{rho}) ")
        return 0

# ------------- Environmental Forces Calculation -----------------------------
def block_HydroStatic_pressure(block:cls.block,Tlc:float,rho:float):
    '''
    Evaluation of hydrostatic pressure for SEA block
    '''
    P = [0]*len(block.pressure_coords)
    if block.space_type == 'SEA':
        for i,point in enumerate(block.pressure_coords):
            if point[1]<= Tlc:
                P[i]=hydrostatic_pressure(point[1],Tlc,rho)
        block.Pressure['STATIC'] = P
    else:
        c_warn(f'physics.py/block_HydroStatic_pressure: Does not support block of type {block.space_type}')
        pass
    return P


def HSM_wave_pressure(cons_:list[float],_1_:bool,block:cls.block):
    '''
    Calculates the wave pressure in kPa over a plate according to Part 1 Chapter 4 Section 5.
    _1_ -> indicates whether we are interested in the HSM-1 or HSM-2, taking the values True and False respectively
    '''
    fnl = 0.9 # @50% Lbp pp 197

    fxL, fps, fbeta, ft,rho,LBP, B, Cw,Lsc, Tlc, D = cons_

    fh = 3*(1.21-0.66*ft)
    
    kp = {
        0 : lambda fyb_: -0.25*ft*(1+fyb_),
        round(0.3-0.1*ft,4)  : -1,
        round(0.35-0.1*ft,4) :  1,
        round(0.8-0.2*ft,4)  :  1,
        round(0.9-0.2*ft,4)  : -1,
        1.0 : -1         
    }

    kp_c = 0

    ka = 1.0 #@50% Lbp, may introduced the entire formula later 
    l = 0.6*(1+ft)*LBP
    
    fyB = lambda x : 2*x/B
    fyz = lambda y,z : z/Tlc+fyB(y)+1
    Phs = lambda y,z : fbeta*fps*fnl*fh*fyz(y,z)*ka*kp_c*Cw*math.sqrt((l+Lsc-125)/LBP)

    Pw = [None]*len(block.pressure_coords)
    # args = ((stiff_plate.plate.start[1],stiff_plate.plate.start[0]),
    #         (stiff_plate.plate.end[1]  ,stiff_plate.plate.end[0]  ))
    
    if block.space_type == 'SEA': # Weatherdeck has special rules according to Section 5.2.2
        if _1_:
            for i,point in enumerate(block.pressure_coords):#the last 3 coordinates pressure_are rent
                kp_c = lin_int_dict(kp,fxL,fyB(point[0]),suppress=True)
                # print(f'kp_c: {kp_c}')
                hw  = -1*Phs(B/2,Tlc)/rho/G
                if point[1] < Tlc :            
                    Pw[i] = max(-1*Phs(*point),-hydrostatic_pressure(point[1],Tlc,rho))
                elif point[1] >= Tlc and point[1] < Tlc+hw:
                    Pw[i] = Phs(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho) #PW = PW,WL - ρg(z - TLC)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho) #PW = PW,WL - ρg(z - TLC)
                    # print('------ Tlc < x < Tlc+hw----')
                    # print("Wave height : ",hw)
                    # print("Pw,wl : ",hw*rho*G)
                    # print("Hydrostatic Pressure : ",hydrostatic_pressure(point[1],Tlc,rho))
                    # print('---------------------------')
                else:
                    Pw[i] =0
        else:
            for i,point in enumerate(block.pressure_coords):
                kp_c = lin_int_dict(kp,fxL,fyB(point[0]),suppress=True)
                # print(f'kp_c: {kp_c}')
                hw  = Phs(B/2,Tlc)/rho/G
                if point[1] < Tlc :            
                    Pw[i] = max(Phs(*point),-hydrostatic_pressure(point[1],Tlc,rho))
                elif point[1] >= Tlc and point[1] < Tlc+hw:
                    Pw[i] = Phs(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                    # print('------ Tlc < x < Tlc+hw----')
                    # print("Wave height : ",hw)
                    # print("Pw,wl : ",hw*rho*G)
                    # print("Hydrostatic Pressure : ",hydrostatic_pressure(point[1],Tlc,rho))
                    # print('---------------------------')
                else:
                    Pw[i]=0

    elif block.space_type == 'ATM':
        x = 1.0 #Section 5.2.2.4, Studying only the weather deck

        if LBP >= 100:
            Pmin = 34.3 #xl = 0.5
        else:
            Pmin = 14.9+0.195*LBP

        kp_c = lin_int_dict(kp,fxL,fyB(D),suppress=True)
        if _1_:
            hw  = -1*Phs(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] >= Tlc and point[1] < Tlc+hw:
                    Pw[i] = Phs(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
                    Pw[i] = max(Pw[i],Pmin)
                Pw[i] *= x
        else:
            hw  = Phs(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] >= Tlc and point[1] < Tlc+hw:
                    Pw[i] = Phs(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
                    Pw[i] = max(Pw[i],Pmin)
                Pw[i] *= x

    else:
        c_warn('Cannot evaluate External pressures for an internal block.')
    key = 'HSM-1' if _1_ else 'HSM-2'
    block.Pressure[key] = Pw
    return Pw

def BSP_wave_pressure(cons_:list[float],_1_:bool,block:cls.block,Port=True):
    '''
    Calculates the wave pressure over a plate according to Part 1 Chapter 4 Section 5.
    _1_ -> indicates whether we are interested in the BSP-1 or BSP-2, taking the values True and False respectively
    Port -> indicates whether we are working on the Port or Starboard side, taking the values True and False respectively
    '''
    fnl = 0.8 # @50% Lbp pp 202
    
    fxL, fps, fbeta, ft,rho,LBP, B, Cw,Lsc, Tlc, D = cons_
    

    l = 0.2*(1+2*ft)*LBP
    
    fyB = lambda y : 2*y/B
    # for the time being it can be left like this as a symmetrical case focused on Port
    if Port:
        fyz = lambda y,z : 2*z/Tlc+2.5*fyB(y)+0.5 #worst case scenario 
    else:
        print('Dont mess with the Port Setting. For the time being...')
        pass
        
    Pbsp = lambda y,z : 4.5*fbeta*fps*fnl*fyz(y,z)*Cw*math.sqrt((l+Lsc-125)/LBP)

    Pw = [None]*len(block.pressure_coords)
    # args = ((stiff_plate.plate.start[1],stiff_plate.plate.start[0]),
    #         (stiff_plate.plate.end[1]  ,stiff_plate.plate.end[0]  ))
    if block.space_type == 'SEA': # Weatherdeck has special rules according to Section 5.2.2
        if _1_:
            hw  = Pbsp(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] < Tlc :            
                    Pw[i] = max(Pbsp(*point),-hydrostatic_pressure(point[1],Tlc,rho/G))
                    # PwS[i] = max(Pbsp(-point[0],point[1]),-hydrostatic_pressure(point[1],Tlc,rho/G))
                elif point[1] >= Tlc and point[1] < Tlc+hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho/G)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho/G)
                else:
                    Pw[i]=0
        else:
            hw  = -Pbsp(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] < Tlc :            
                    Pw[i] = max(-Pbsp(*point),-hydrostatic_pressure(point[1],Tlc,rho))
                elif point[1] >= Tlc and point[1] < Tlc+hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                else:
                    Pw[i]=0
    elif block.space_type == 'ATM':
        x = 1.0 #Section 5.2.2.4, Studying only the weather deck

        if LBP >= 100:
            Pmin = 34.3 #xl = 0.5
        else:
            Pmin = 14.9+0.195*LBP

        hw  = Pbsp(B/2,Tlc)/rho/G
        if _1_:
            hw  = Pbsp(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] >= Tlc and point[1] < Tlc+hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
                Pw[i]*=x
        else:
            hw  = -Pbsp(B/2,Tlc)/rho/G
            for i,point in enumerate(block.pressure_coords):
                if point[1] >= Tlc and point[1] < Tlc+hw:
                    # Pw[i] = Pbsp(point[0],Tlc) + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = hw*rho*G + hydrostatic_pressure(point[1],Tlc,rho)
                    Pw[i] = max(Pw[i],Pmin)
                else:
                    Pw[i]=0
                Pw[i]*=x
    if Port:
        key = 'BSP-1P' if _1_ else 'BSP-2P'
    else:
        key = 'BSP-1S' if _1_ else 'BSP-2S'

    block.Pressure[key] = Pw
    return Pw
#------------------------------------------------------------------------------
#--------------- Internal Forces Calculation ----------------------------------
def StaticLiquid_Pressure(block:cls.block,debug=False):
    '''
    Static Liquid Pressure : Normal Operations at sea and Harbour/Sheltered water operations\n
    To access the Normal Operations at sea component use the key 'S-NOS' and the key 'S-HSWO' for the \n
    Harbour/Sheltered water operations.

    '''
    # Ppv : Design vapour Pressure not to be taken less than 25 kPa
    # When the Code is made universal for Dry and Tankers it shall be taken to consideration
    #For the time is left as it is. IF AN LC BLOCK IS CREATED THE RESULT WILL BE USELESS
    if block.space_type == "LC": liquid_cargo = True
    elif block.space_type == 'DC': return [None,None]
    else: liquid_cargo = False

    P_nos = [None]*len(block.pressure_coords)
    P_hswo = [None]*len(block.pressure_coords)
    Ztop = max(block.coords,key= lambda x : x[1])[1]

    
    if liquid_cargo: 
        F_nos = lambda z  :hydrostatic_pressure(z,Ztop,block.payload['rho'])+block.payload['Ppv']
        # F_hswo = lambda z :hydrostatic_pressure(z,Ztop,block.payload['rho'])+block.payload['Ppv']
    else:
        F_nos = lambda z  :hydrostatic_pressure(z,(Ztop+block.payload['hair']/2),block.payload['rho'])
        # F_hswo = lambda z :hydrostatic_pressure(z,(Ztop+block.payload['hair']/2),block.payload['rho'])# extra case for ballast tank seems redundant for the time being

        
    for i,point  in enumerate(block.pressure_coords):
        P_nos[i]= F_nos(point[1])
        # P_hswo.append(F_hswo(point[1]))

    # block.Pressure['S-NOS'] = P_nos
    # block.Pressure['S-HSWO'] = P_hswo
    block.Pressure['STATIC_IN'] = P_nos
    return P_nos

def DynamicLiquid_Pressure(block:cls.block,case:PhysicsData,debug=False):
    '''
    Dynamic Liquid Pressure: Evaluates the pressure distribution due to the dynamic motion of a fluid inside\n
    a tank.
    '''
    def  ref_eval(block:cls.block,a:tuple):
        '''
        V j = aX ( xj – x G ) + aY ( y j – y G ) + ( aZ + g ) ( zj – zG )

        '''
        Max = 0
        V = lambda x,y,z : a[0]*(x-block.CG[0]) + a[1]*(y-block.CG[1])+(a[2]+G)*(z-block.CG[2])
        pos =  []
        for i,point  in enumerate(block.pressure_coords):
            temp = V(*(case.Lsc*case.fxL,*point))
            if temp > Max: pos = point
        
        return (block.CG[0],*pos)
    

    ax,ay,az = case.accel_eval(block.CG)#221
    x0,y0,z0 = ref_eval(block,(ax,ay,az))
    if debug:
        print('ax : ',ax,' ay : ',ay,' az : ',az)
        print('x0 : ',x0,' y0 : ',y0,' z0 : ',z0)
    
    #strength assessment only
    if block.space_type == "LC": 
        full_l = 0.62
        full_t = 0.62
    else: 
        full_l = 1.0
        full_t = 1.0

    P = [None]*len(block.pressure_coords)
    Pld = lambda x,y,z: case.fb*block.payload['rho']*(az*(z0-z)+full_l*ax*(x0-x)+full_t*ay*(y0-y))
    
    for i,point in enumerate(block.pressure_coords):
        P[i] = Pld(*(case.Lsc*case.fxL,*point))

    block.Pressure[case.int_cond] = P
    return P

def DynamicDryCargo_Pressure(block:cls.block,case:PhysicsData,debug=False):
    '''
    Dynamic Dry Cargo Pressure: Evaluates the pressure distribution due to the dynamic movements of the ship.
    \nWe assume that the ship is homogeneously loaded with Fully Filled Cargo (table 1 page 227, CSR Part 1 Chapter 4 Section 6)

    '''
    zc = block.pressure_coords[0][1] # max of the coordinates may be redundant as there is a specific order the plates shall be (clockwise)
    
    rho  = block.payload['rho'] if (block.payload['rho']>=1.0) else 1.0
    def Pbd(x,y,z,ax,ay,az,Kc):
        if z <= zc:
            return case.fb*rho*(Kc*az*(block.CG[2]-z)+0.25*ax*(block.CG[0]-x)+0.25*ay*(block.CG[1]-y))
        else:
            return 0

    ax,ay,az = case.accel_eval(block.CG)#221
    P = [None]*len(block.pressure_coords)

    for i,point in enumerate(block.pressure_coords):
        P[i] = Pbd(block.CG[0],*point,ax,ay,az,block.Kc[i])
    
    block.Pressure[case.int_cond] = P
    return P

def StaticDryCargo_Pressure(block:cls.block,debug=False):
    '''
    Static Dry Cargo Pressure: Evaluates the pressure distribution of the static load applied by the cargo to the stiffened plates.
    \nWe assume that the ship is homogeneously loaded with Fully Filled Cargo (table 1 page 227, CSR Part 1 Chapter 4 Section 6)
    '''
    
    zc = block.pressure_coords[0][1] # max of the coordinates may be redundant as there is a specific order the plates shall be (clockwise)
    
    rho  = block.payload['rho'] if (block.payload['rho']>=1.0) else 1.0
    def static(z,Kc):
        if z <= zc:
            return G*rho*Kc*(block.CG[2]-z)
        else:
            return 0

    P = [None]*len(block.pressure_coords)

    for i,point in enumerate(block.pressure_coords):
        P[i] = static(point[1],block.Kc[i])
    
    block.Pressure['STATIC_IN'] = P
    return P
#------------------------------------------------------------------------------
#------- Total Evaluation of Pressure Distribution ----------------------------

def Dynamic_total_eval(ship:cls.ship,Tlc:float,case:str,LOG = True):
    if case in ('BSR','BSP','OSA','OST'):
        _1,_2 = '-1P','-2P'
    elif case in ('HSM','HSA','FSM'):
        _1,_2 = '-1','-2'
    else:
        c_error(f'(physics.py) Dynamic_total_eval: {case} is not a valid Dynamic condition. The available conditions are ; HSM, HSA, FSM, BSR, BSP,OST,OSA.')
        quit()

    case_1 = PhysicsData(Tlc,ship,case+_1)
    case_2 = PhysicsData(Tlc,ship,case+_2)
    for c in (case_1,case_2):
        for i in ship.blocks:
            if i.space_type == 'SEA' or i.space_type == 'ATM': 
                F = c.wave_pressure
                def args(x): return (x.external_loadsC(),'1' in  x.cond,i)
            elif i.space_type == 'DC':
                F = DynamicDryCargo_Pressure
                def args(x): return (i,x,False)
            else: 
                F = DynamicLiquid_Pressure
                def args(x): return (i,x,False)
        
            Pd = F(*args(c))
            if (None not in Pd) and LOG:
                
                c_success(f'{c.cond} CASE STUDY:\nCalculated block: ',i)
                c_success(' ---- X ----  ---- Y ----  ---- P ----',default=False)
                [c_success(f'{round(i.pressure_coords[j][0],4): =11f}  {round(i.pressure_coords[j][1],4): =11f} {round(Pd[j],4): =11f}',default=False) for j in range(len(Pd))]
    return case_1,case_2

def Static_total_eval(ship:cls.ship,Tlc:float,rho:float,LOG = True):
    for i in ship.blocks:
        if i.space_type == 'SEA': 
            F = block_HydroStatic_pressure
            args =(i,Tlc,rho)
        elif i.space_type == 'DC':
            F = StaticDryCargo_Pressure
            args = (i,False)
        elif i.space_type =='ATM':continue
        else: 
            F = StaticLiquid_Pressure
            args = (i,False)
    
        Pd = F(*args)
        if (None not in Pd) and LOG:
            
            c_success(f'STATIC CASE STUDY:\nCalculated block: ',i)
            c_success(' ---- X ----  ---- Y ----  ---- P ----',default=False)
            [c_success(f'{round(i.pressure_coords[j][0],4): =11f}  {round(i.pressure_coords[j][1],4): =11f} {round(Pd[j],4): =11f}',default=False) for j in range(len(Pd))]

