# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 18:30:31 2018

@author: Pelumi
"""

"""This is the input page for Composition properties to PVT page"""

import tkinter as tk
from tkinter import ttk
            
class LabelInput(tk.Frame):
    """A widget containing a label and input together"""
    
    def __init__(self,parent,label="",input_class=tk.Spinbox,input_var=None,input_args=None,label_args=None,**kwargs):
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
        print(self.input.grid(row=0,column=1,sticky=(tk.W+tk.E)))
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
            self.input.insert('1.0'.value)
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
        self.reset()
        
    def get(self):
        data={}
        for key,widget in self.inputs.items():
            data[key]=widget.get()
        return data
    
    def reset(self):
        for widget in self.inputs.values():
            widget.set('')
            
            
        
class my_application(tk.Tk):
    """XPVT ML"""
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.title("PVT ML")
        self.geometry("400x300")
        self.resizable(width=False,height=False)
        
        #Defining the UI
        self.cruise=CompositionInput(self)
        self.cruise.grid(row=0, padx=10)
        
if __name__ == "__main__":
    app=my_application()
    app.mainloop()
            
        