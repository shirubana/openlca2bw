# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 22:16:06 2021

@author: cyrille.francois
"""
import olca
import pyprind
import json
from ..utils import return_attribute, uncertainty_convert
from bw2io import normalize_units as normalize_unit


def json_elementary_flow(self):
    flows = list(self.get_all(olca.Flow))
    flow_ref_unit = self.flow_unit
    ElemFlowList = []
    pbar = pyprind.ProgBar(len(flows), title="Extracting "+str(len(flows))+" flows from OpenLCA:")
    for f in flows:
        pbar.update(item_id = flows.index(f)+1)
        if f.flow_type.name == 'ELEMENTARY_FLOW':
            if f.category.category_path is None:
                type = f.category.name
                cat = (type,'unspecified')
            elif len(f.category.category_path) == 1:
                type = f.category.category_path[0].lower()
                cat = (type,f.category.name)
            elif f.category.category_path[1] == 'Resource':
                type = 'natural resource'
                cat = (type,f.category.name)
            elif f.category.category_path[1].split()[0] == 'Emission':
                type = 'emission'
                cat = (f.category.category_path[1].split()[-1],f.category.name)
            else:
                type = f.category.category_path[1].lower()
                cat = (type,f.category.name)
            ElemFlowList.append({
                "categories": cat,
                "code": f.id,
                "CAS number": f.cas,
                "database": "biosphere3",
                "name": f.name,
                "type": type,
                "unit": flow_ref_unit.loc[f.flow_properties[0].flow_property.id].values[0]
            })
    json_object = json.dumps(ElemFlowList, indent = 4)
    print(pbar)
    return(json_object)

def list_methods(self):
    methods = list(self.get_all(olca.ImpactMethod))
    conv_units = self.unit_conv
    pbar = pyprind.ProgBar(len(methods), title="Extracting "+str(len(methods))+" LCIA methods from OpenLCA:")
    list_methods = []
    for m in methods:
        pbar.update(item_id = m.name)
        impact_categories = m.impact_categories
        for c in impact_categories:
            cate = self.get(olca.ImpactCategory,model_id=c.id)
            name = (m.name,cate.name)
            ref_unit = cate.reference_unit_name
            list_cf = []
            impact_factors = cate.impact_factors
            for i in impact_factors:
                list_cf.append((
                    ('biosphere3',i.flow.id),
                    i.value / conv_units.loc[i.unit.id].values[0]
                  ))
            list_methods.append({
                'name': name,
                'ref_unit': ref_unit,
                'list_cf': list_cf
                })
    print(pbar)
    return(list_methods)

def list_nonuser_process(self, database_name = 'EcoInvent', nonuser_folders = []):
    processes = self.get_descriptors(olca.Process)
    conv_loc = self.location_table
    list_nonuser = []
    for p in processes:
        if p.category_path[0] in nonuser_folders:
            list_nonuser.append(p.id)
    pbar = pyprind.ProgBar(len(list_nonuser), title="Extracting "+str(len(list_nonuser))+" non-user processes from OpenLCA:")
    list_process = []
    list_process_parameters = []
    for i in list_nonuser:
        p_json = self.get(olca.Process,model_id=i).to_json()
        pbar.update(item_id = list_nonuser.index(i)+1)
        classif = [return_attribute(p_json, ('category','name'))]
        classif.insert(0,return_attribute(p_json, ('category','categoryPath')))
        exch = return_attribute(p_json,'exchanges')
        ref_exch = [exc for exc in exch if return_attribute(exc,'quantitativeReference')][0]
        if return_attribute(ref_exch,('flow','flowType')) == 'WASTE_FLOW':
            cf_waste = -1
        else:
            cf_waste = 1
        p_arg = {'comment': return_attribute(p_json, 'description'),
                 'classification': classif,
                 'activity': return_attribute(p_json,'@id'),
                 'location': conv_loc.loc[return_attribute(p_json,('location','@id'))].values[0],
                 'name': return_attribute(p_json,'name'),
                 'parameters': return_attribute(p_json,'parameters'),
                 'authors': return_attribute(p_json,('processDocumentation','dataGenerator','name')),
                 'type': 'process',
                 'code': return_attribute(p_json,'@id'),
                 'reference product': return_attribute(ref_exch,('flow','name')),
                 'flow': return_attribute(ref_exch,('flow','@id')),
                 'unit': normalize_unit(return_attribute(ref_exch,('unit','name'))),
                 'unit_id': return_attribute(ref_exch,('unit','@id')),
                 'production amount': return_attribute(ref_exch,'amount') * cf_waste
                 }
        list_exc = []
        for exc in exch:
            cf_IO = 1
            if return_attribute(exc,('flow','flowType')) == 'WASTE_FLOW':
                if return_attribute(exc,'input') == False:
                    cf_IO = -1
                else:
                    if return_attribute(exc,'quantitativeReference'):
                        cf_IO = -1
                    elif return_attribute(exc,'avoidedProduct') == False:
                        print("Coproduct "+str(return_attribute(exc,('flow','name')))+" related to process "+str(return_attribute(p_json,'name'))+"unspecified avoided\nExchange not extracted in brightway !!!")
                        continue
            if return_attribute(exc,('flow','flowType')) == 'ELEMENTARY_FLOW':
                if return_attribute(exc,'input') == True and return_attribute(exc,('flow','categoryPath'))[1] != 'Resource':
                    cf_IO = -1
            if return_attribute(exc,('flow','flowType')) == 'PRODUCT_FLOW' and return_attribute(exc,'input') == False:
                if return_attribute(exc,'quantitativeReference'):
                    cf_IO = 1
                elif return_attribute(exc,'avoidedProduct'):
                    cf_IO = -1
                else:
                    print("Coproduct "+str(return_attribute(exc,('flow','name')))+" related to process "+str(return_attribute(p_json,'name'))+"unspecified avoided\nExchange not extracted in brightway !!!")
                    continue
            exc_arg = {
                'flow': return_attribute(exc,('flow','@id')),
                'name': return_attribute(exc,('flow','name')),
                'unit': normalize_unit(return_attribute(exc,('unit','name'))),
                'unit_id': return_attribute(exc,('unit','@id')),
                'comment': return_attribute(exc,'descrition'),
                'formula': return_attribute(exc,'amountFormula'),
                'amount': return_attribute(exc,'amount') * cf_IO
                }
            if return_attribute(exc,'quantitativeReference'):
                exc_arg.update({'type': 'production',
                                'input': (database_name,return_attribute(p_json,'@id'))
                                })
            elif return_attribute(exc,('flow','flowType')) == 'ELEMENTARY_FLOW':
                exc_arg.update({'type': 'biosphere',
                                'input': ('biosphere3',return_attribute(exc,('flow','@id')))
                                })
            else:
                if  return_attribute(exc,'defaultProvider') is None:
                        print("No provider for flow "+str(return_attribute(exc,('flow','name')))+" related to process "+str(return_attribute(p_json,'name'))+"\nExchange not extracted !!!")
                        continue
                else:
                    exc_arg.update({'type': 'technosphere',
                                    'input': (database_name,return_attribute(exc,('defaultProvider','@id'))),
                                    'activity': return_attribute(exc,('defaultProvider','@id'))
                                    })
            if return_attribute(exc,'dqEntry') is not None:
                exc_arg.update({'pedigree': {
                    'reliability': return_attribute(exc,('dqEntry',1)),
                    'completeness': return_attribute(exc,('dqEntry',3)),
                    'temporal correlation': return_attribute(exc,('dqEntry',5)),
                    'geographical correlation': return_attribute(exc,('dqEntry',7)),
                    'further technological correlation': return_attribute(exc,('dqEntry',9))}
                })
            if return_attribute(exc,'uncertainty') is not None:
                uncertainties = uncertainty_convert(return_attribute(exc,'uncertainty'))
                if uncertainties is not None:
                    exc_arg.update(uncertainty_convert(return_attribute(exc,'uncertainty')))
            exc_arg = {k: v for k, v in exc_arg.items() if v}
            list_exc.append(exc_arg)
        p_arg.update({'exchanges': list_exc}) 
        list_process.append(p_arg)
        if return_attribute(p_json,'parameters') is not None:
            list_process_parameters.append(((database_name,return_attribute(p_json,'@id')), [p['@id'] for p in return_attribute(p_json,'parameters')]))
    print(pbar)
    return list_process, list_process_parameters


def extract_list_process(self, databases_names, list_nonuser_id, db_nonuser_name = 'EcoInvent'):
    processes = list(self.get_descriptors(olca.Process))
    conv_loc = self.location_table
    db_names = list(databases_names.keys())
    db_data = []
    db_list_id = []
    for db in db_names:
        list_process_id = []
        for p in processes:
            if p.category_path is None:
                if None in databases_names[db]:
                    list_process_id.append(p.id)
            else:
                if p.category_path[0] in databases_names[db]:
                    list_process_id.append(p.id)
        db_list_id.append(list_process_id)
    db_list_id = dict(zip(db_names,db_list_id))
    list_process_parameters = []
    for db in db_names:    
        pbar = pyprind.ProgBar(len(db_list_id[db]), title="Extracting "+str(len(db_list_id[db]))+" processes from OpenLCA for "+str(db)+" database:")    
        list_process = []
        for i in db_list_id[db]:
            p_json = self.get(olca.Process,model_id=i).to_json()
            pbar.update(item_id = db_list_id[db].index(i)+1)
            classif = [return_attribute(p_json, ('category','name'))]
            classif.insert(0,return_attribute(p_json, ('category','categoryPath')))
            exch = return_attribute(p_json,'exchanges')
            ref_exch = [exc for exc in exch if return_attribute(exc,'quantitativeReference')][0]
            p_arg = {'comment': return_attribute(p_json, 'description'),
                     'classification': classif,
                     'activity': return_attribute(p_json,'@id'),
                     'name': return_attribute(p_json,'name'),
                     'parameters': return_attribute(p_json,'parameters'),
                     'authors': return_attribute(p_json,('processDocumentation','dataGenerator','name')),
                     'type': 'process',
                     'code': return_attribute(p_json,'@id'),
                     'reference product': return_attribute(ref_exch,('flow','name')),
                     'flow': return_attribute(ref_exch,('flow','@id')),
                     'unit': normalize_unit(return_attribute(ref_exch,('unit','name'))),
                     'unit_id': return_attribute(ref_exch,('unit','@id')),
                     'production amount': return_attribute(ref_exch,'amount')
                     }
            if return_attribute(p_json,('location','@id')) is not None:
                p_arg.update({'location': conv_loc.loc[return_attribute(p_json,('location','@id'))].values[0]})
            list_exc = []
            for exc in exch:
                cf_IO = 1
                if return_attribute(exc,('flow','flowType')) == 'WASTE_FLOW':
                    if return_attribute(exc,'input') == False:
                        cf_IO = -1
                    else:
                        if return_attribute(exc,'quantitativeReference'):
                           cf_IO = -1
                        elif return_attribute(exc,'avoidedProduct') == False:
                            print("Coproduct "+str(return_attribute(exc,('flow','name')))+" related to process "+str(return_attribute(p_json,'name'))+"unspecified avoided\nExchange not extracted in brightway !!!")
                            continue
                if return_attribute(exc,('flow','flowType')) == 'ELEMENTARY_FLOW':
                    if return_attribute(exc,'input') == False and return_attribute(exc,('flow','categoryPath'))[1] == 'Resource':
                        cf_IO = -1
                    if return_attribute(exc,'input') == True and return_attribute(exc,('flow','categoryPath'))[1] != 'Resource':
                        cf_IO = -1
                if return_attribute(exc,('flow','flowType')) == 'PRODUCT_FLOW' and return_attribute(exc,'input') == False:
                    if return_attribute(exc,'quantitativeReference'):
                        cf_IO = 1
                    elif return_attribute(exc,'avoidedProduct'):
                        cf_IO = -1
                    else:
                        print("Coproduct "+str(return_attribute(exc,('flow','name')))+" related to process "+str(return_attribute(p_json,'name'))+"unspecified avoided\nExchange not extracted in brightway !!!")
                        continue
                exc_arg = {
                    'flow': return_attribute(exc,('flow','@id')),
                    'name': return_attribute(exc,('flow','name')),
                    'unit': normalize_unit(return_attribute(exc,('unit','name'))),
                    'unit_id': return_attribute(exc,('unit','@id')),
                    'comment': return_attribute(exc,'descrition'),
                    'formula': return_attribute(exc,'amountFormula'),
                    'amount': return_attribute(exc,'amount') * cf_IO
                    }
                if return_attribute(exc,'quantitativeReference'):
                    exc_arg.update({'type': 'production',
                                    'input': (db,return_attribute(p_json,'@id'))
                                    })
                elif return_attribute(exc,('flow','flowType')) == 'ELEMENTARY_FLOW':
                    exc_arg.update({'type': 'biosphere',
                                    'input': ('biosphere3',return_attribute(exc,('flow','@id')))
                                    })
                else:
                    if  return_attribute(exc,'defaultProvider') is None:
                        print("No provider for flow "+str(return_attribute(exc,('flow','name')))+" related to process "+str(return_attribute(p_json,'name'))+"\nExchange not extracted !!!")
                        continue
                    else:
                        exc_arg.update({'type': 'technosphere',
                                        'activity': return_attribute(exc,('defaultProvider','@id'))
                                        })
                        if return_attribute(exc,('defaultProvider','@id')) in list_nonuser_id:
                            exc_arg.update({'input': (db_nonuser_name,return_attribute(exc,('defaultProvider','@id')))})
                        else:
                            exc_arg.update({'input': ([name for name in list(db_list_id.keys()) if return_attribute(exc,('defaultProvider','@id')) in db_list_id[db]][0],return_attribute(exc,('defaultProvider','@id')))})
                if return_attribute(exc,'dqEntry') is not None:
                    exc_arg.update({'pedigree': {
                        'reliability': return_attribute(exc,('dqEntry',1)),
                        'completeness': return_attribute(exc,('dqEntry',3)),
                        'temporal correlation': return_attribute(exc,('dqEntry',5)),
                        'geographical correlation': return_attribute(exc,('dqEntry',7)),
                        'further technological correlation': return_attribute(exc,('dqEntry',9))}
                    })
                if return_attribute(exc,'uncertainty') is not None:
                    uncertainties = uncertainty_convert(return_attribute(exc,'uncertainty'))
                    if uncertainties is not None:
                        exc_arg.update(uncertainty_convert(return_attribute(exc,'uncertainty')))
                exc_arg = {k: v for k, v in exc_arg.items() if v}
                list_exc.append(exc_arg)
            p_arg.update({'exchanges': list_exc}) 
        list_process.append(p_arg)
        if return_attribute(p_json,'parameters') is not None:
            list_process_parameters.append(((db,return_attribute(p_json,'@id')), [p['@id'] for p in return_attribute(p_json,'parameters')]))
        db_data.append(list_process)
        print(pbar)
    return dict(zip(db_names, db_data)), list_process_parameters


