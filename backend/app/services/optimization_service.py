import pandas as pd
import numpy as np

class OptimizationService:
    @staticmethod
    def run_optimization(pv_df: pd.DataFrame, price_data: list, bess_power_mw: float, bess_capacity_mwh: float):
        """
        Runs a simplified heuristic dispatch for PV + BESS.
        """
        # 1. Prepare Data
        # Ensure we have matching lengths (min of both)
        limit = min(len(pv_df), len(price_data))
        
        df = pv_df.iloc[:limit].copy()
        prices = [p['price'] for p in price_data[:limit]] # Assuming price_data is list of dicts from entsoe_service
        df['price_eur_mwh'] = prices
        
        # 2. Heuristic Logic
        # "Smart Dispatch": 
        # - Calculate daily average price.
        # - Charge when (Price < DailyAvg * 0.8) and (PV > 0 or Grid Charge allowed)
        # - Discharge when (Price > DailyAvg * 1.2)
        # - Otherwise Self-Consume PV or Idle.
        
        # Parameters
        soc_kwh = 0.0
        max_soc_kwh = bess_capacity_mwh * 1000
        max_power_kw = bess_power_mw * 1000
        efficiency = 0.9
        
        bess_flow_kw = [] # + Discharge, - Charge
        final_soc_kwh = []
        
        for i, row in df.iterrows():
            price = row['price_eur_mwh']
            pv = row['pv_power_kw']
            
            # Simple decision (this is where the MILP would normally be)
            # Just a placeholder logic for now to show 'Action'
            
            flow = 0.0
            
            # Charge logic: Cheap price, or Excess PV? 
            # For simplicity: If price is negative or very low (arbitrary threshold like 20 EUR), charge at max power
            if price < 20: 
                # Charge from Grid or PV
                charge_power = min(max_power_kw, (max_soc_kwh - soc_kwh) / efficiency)
                flow = -charge_power
            elif price > 100 and soc_kwh > 0:
                # Discharge if expensive
                discharge_power = min(max_power_kw, soc_kwh * efficiency)
                flow = discharge_power
            else:
                # If PV is generating, and we have space, store it?
                # This is the "Cannibalization" mitigation
                pass
                
            # Update SoC
            if flow < 0: # Charging
                soc_kwh += abs(flow) * efficiency
            else: # Discharging
                discharged_energy = flow
                soc_kwh -= discharged_energy / efficiency 
                # Track discharge for cycle counting (Ah throughput or energy throughput)
                # Cycle = Total Discharged Energy / Capacity
                # We'll sum it up later.
            
            soc_kwh = max(0, min(soc_kwh, max_soc_kwh))
            
            bess_flow_kw.append(flow)
            # Store positive discharge for summing later
            # flow is positive when discharging in this convention?
            # optimization_service.py:51 -> flow = discharge_power (positive)
            # optimization_service.py:48 -> flow = -charge_power (negative)

            final_soc_kwh.append(soc_kwh)
            
        df['bess_flow_kw'] = bess_flow_kw
        df['soc_kwh'] = final_soc_kwh
        df['net_grid_kw'] = df['pv_power_kw'] + df['bess_flow_kw']
        
        # 3. Financials
        # Revenue = NetGrid (Export) * Price (if Export > 0)
        # Cost = NetGrid (Import) * Price (if Export < 0)
        
        df['revenue'] = df.apply(lambda x: (x['net_grid_kw']/1000) * x['price_eur_mwh'] if x['net_grid_kw'] > 0 else 0, axis=1)
        # We ignore import cost for this simple revenue calc, or subtract it? 
        # PRD says "Revenue", assume Net Revenue.
        df['cost'] = df.apply(lambda x: abs(x['net_grid_kw']/1000) * x['price_eur_mwh'] if x['net_grid_kw'] < 0 else 0, axis=1)
        
        total_revenue = df['revenue'].sum() - df['cost'].sum()
        
        # Calculate Cycles
        # Cycle = Total Energy Discharged (MWh) / Nameplate Capacity (MWh)
        total_discharge_kwh = df[df['bess_flow_kw'] > 0]['bess_flow_kw'].sum()
        total_cycles = total_discharge_kwh / (bess_capacity_mwh * 1000) if bess_capacity_mwh > 0 else 0

        return {
            "financials": {
                 "total_revenue_eur": round(total_revenue, 2),
                 "annual_pv_production_mwh": round(df['pv_power_kw'].sum()/1000, 2),
                 "annual_cycles": round(total_cycles, 1)
            },
            "hourly_data": df.head(168).to_dict(orient='records') # Return first 1 week for chart
            # 168 hours = 7 days
        }

optimization_service = OptimizationService()
