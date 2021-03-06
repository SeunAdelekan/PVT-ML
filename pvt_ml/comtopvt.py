# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 18:30:31 2018

@author: Pelumi
"""

"""This is the input page for Composition properties to PVT page"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import csv
from decimal import Decimal, InvalidOperation       

class ValidatedMixin:
    """Adds a validation functionality to an input widget"""
    def __init__(self,*arg,error_var=None,**kwargs):
        self.error=error_var or tk.StringVar()
        super().__init__(*arg,**kwargs)

        vcmd=self.register(self._validate)
        invcmd=self.register(self._invalid)

        self.config(validate='all',validatecommand=(vcmd,'%P','%s','%S','%V','%i','%d'),invalidcommand=(invcmd,'%P','%s','%S','%V','%i','%d'))

    def _toggle_error(self, on=False):
        self.config(foreground=('red' if on else 'black'))

    def _validate(self,proposed,current,char,event,index,action):
        self._toggle_error(False)
        self.error.set('')
        valid=True
        if event =='focusout':
            valid=self._focusout_validate(event=event)
        elif event =='key':
            valid=self._key_validate(proposed=proposed, current=current,char=char,event=event, index=index, action=action)
        return valid
    
    def _focusout_validate(self,**kwargs):
        return True

    def _key_validate(self,**kwargs):
        return True
    
    def _invalid(self,proposed,current,char,event,index,action):
        if event =='focusout':
            self._focusout_invalid(event=event)
        elif event =='key':
            self._key_invalid(proposed=proposed, current=current,char=char,event=event, index=index, action=action)
    
    def _focusout_invalid(self,**kwargs):
        self._toggle_error(True)

    def _key_invalid(self,**kwargs):
        pass    

    def trigger_focusout_validation(self):
        valid=self._validate("","","","focusout","","")
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid

class ValidatedSpinbox(ValidatedMixin,tk.Spinbox):
    
    def __init__(self,*args,min_var=None,max_var=None,focus_update_var=None,from_='Infinity',to='Infinity',**kwargs):
        super().__init__(*args,from_=from_,to=to,**kwargs)
        self.resolution=Decimal(str(kwargs.get('increment','1.0')))
        self.precision=(self.resolution.normalize().as_tuple().exponent)

    def _key_validate(self,char,index,current,proposed,action,**kwargs):
        valid=True
        min_val=self.cget('from')
        max_val=self.cget('to')
        no_negative=min_val>=0
        no_decimal=self.precision >= 0
        if action =='0':
            return True
        #First, filter out obviously invalid keystrokes
        if any([(char not in('-12345678.')),(char =='-' and (no_negative or index!='0')),(char=='.' and (no_decimal or '.' in current))]):
            return False

        #At this point, proposed is either '-','.','-.', or a valid Decimal String
        if proposed in '-.':
            return True
        #Proposed is a valid Decimal String convert to Decimal and Check more:
        proposed = Decimal(proposed)
        proposed_precision=proposed.as_tuple().exponent

        if any([(proposed>max_val),(proposed_precision<self.precision)]):
            return False

        return valid
    def _focusout_validate(self,**kwargs):
        valid=True
        value=self.get()
        min_val=self.cget('from')

        try:
            value=Decimal(value)
        except InvalidOperation:
            self.error.set('Invalid number string: {}'.format(value))
            return False
        
        if value<min_val:
            self.error.set('Value is too low(min {})'.format(min_val))
            valid =False
        return valid

class LabelInput(tk.Frame):
    """A widget containing a label and input together"""
    
    def __init__(self,parent,label="",input_class=ValidatedSpinbox,input_var=None,input_args=None,label_args=None,**kwargs):
        super().__init__(parent,**kwargs)
        input_args=input_args or {}
        label_args=label_args or {}
        self.variable=input_var
        
        if input_class in (ttk.Checkbutton,ttk.Button,ttk.Radiobutton):
            input_args["text"]=label
            input_args["variable"]=input_var
        else:
            self.label=ttk.Label(self,text=label,**label_args)
            self.label.grid(row=0,column=0,sticky=(tk.W+tk.E))
            input_args["textvariable"]=input_var
            
        self.input= input_class(self,**input_args)
        self.input.grid(row=0,column=1,sticky=(tk.W+tk.E))
        self.columnconfigure(0,weight=1)
            
    def grid(self,sticky=(tk.E+tk.W),**kwargs):
        super().grid(sticky=sticky,**kwargs)
    
    def get(self):
        try:
            if self.variable:
                return self.variable.get()
            elif type(self.input) == tk.Text:
                return self.input.get('1.0',tk.END)
            else:
                return self.input.get()
        except (TypeError, tk.TclError):
            # happens when numeric firelds are empty.
            return ''
    
    def set(self,value,*args,**kwargs):
        if type(self.variable) == tk.BooleanVar:
            self.variable.set(bool(value))
        elif self.variable:
            self.variable.set(value,*args,**kwargs)
        elif type(self.input) in (ttk.Checkbutton, ttk.Radiobutton):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif type(self.input) == tk.Text:
            self.input.delete('1.0',tk.END)
            self.input.insert('1.0',value)
        else: #input must be an Entry-type widget with no variable
            self.input.delete(0,tk.END)
            self.input.insert(0,value)
                
class CompositionInput(tk.Frame):
    """The input for our widgets"""
    
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent, *args,**kwargs)
        #A dict to keep track of input widgets
        self.inputs={}
        
        composition=tk.LabelFrame(self,text="Composition")
        
        self.inputs["C1"]=LabelInput(composition,label="C1",input_args={"from_":0.00,"to":100.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs['C1'].grid(row=0,column=0)
        self.inputs["C2"]=LabelInput(composition,label="C2",input_args={"from_":0.00,"to":100.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs["C2"].grid(row=1,column=0)
        self.inputs["C3"]=LabelInput(composition,label="C3",input_args={"from_":0.00,"to":100.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs["C3"].grid(row=2,column=0)
        self.inputs["IC4"]=LabelInput(composition,label="IC4",input_args={"from_":0.00,"to":100.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs["IC4"].grid(row=3,column=0)
        self.inputs["NC4"]=LabelInput(composition,label="NC4",input_args={"from_":0.00,"to":100.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs["NC4"].grid(row=4,column=0)
        self.inputs["IC5"]=LabelInput(composition,label="IC5",input_args={"from_":0.00,"to":100.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs["IC5"].grid(row=5,column=0)
        self.inputs["NC5"]=LabelInput(composition,label="NC5",input_args={"from_":0.00,"to":100.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs["NC5"].grid(row=6,column=0)
        self.inputs["C6"]=LabelInput(composition,label="C6",input_args={"from_":0.00,"to":100.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs["C6"].grid(row=7,column=0)
        self.inputs["C7+"]=LabelInput(composition,label="C7+",input_args={"from_":0.00,"to":100.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs["C7+"].grid(row=8,column=0)
        self.inputs["MW"]=LabelInput(composition,label="MW",input_args={"from_":0.00,"to":500.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs["MW"].grid(row=9,column=0)
        self.inputs["MW(C7+)"]=LabelInput(composition,label="MW(C7+)",input_args={"from_":0.00,"to":500.0,"increment":0.01},input_var=tk.DoubleVar())
        self.inputs["MW(C7+)"].grid(row=10,column=0)
        composition.grid(row=1,column=0)

        self.selection={}
        predict_choice=tk.LabelFrame(self,text="Selection")
        predict_desc=ttk.Label(predict_choice, text="PVT Properties to be predicted")
        predict_desc.grid(row=0,column=0,columnspan=2,sticky=tk.W)
        self.selection["bub_point"]=LabelInput(predict_choice,label="Bubble Point",input_class=ttk.Checkbutton,input_var=tk.BooleanVar())
        self.selection["bub_point"].grid(row=1,column=0)
        self.selection["sol_ratio"]=LabelInput(predict_choice,label="Solution Gas Oil Ratio",input_class=ttk.Checkbutton,input_var=tk.BooleanVar())
        self.selection["sol_ratio"].grid(row=1,column=1)
        self.selection["oil_visc"]=LabelInput(predict_choice,input_class=ttk.Checkbutton,label="Oil Viscosity",input_var=tk.BooleanVar())
        self.selection["oil_visc"].grid(row=2,column=0)
        self.selection["fvf"]=LabelInput(predict_choice,input_class=ttk.Checkbutton,label="Formation Volume Factor",input_var=tk.BooleanVar())
        self.selection["fvf"].grid(row=2,column=1)
        predict_choice.grid(row=0,column=0)

        self.reset()

    def get(self):
        data={}
        for key,widget in self.inputs.items():
            data[key]=widget.get()
        return data
    
    def gett(self):
        select={}
        for key,widget in self.selection.items():
            select[key]=widget.get()
        return select
        
    def reset(self):
        for widget in self.inputs.values():
            widget.set('')
        for widget in self.selection.values():
            widget.set('')
    