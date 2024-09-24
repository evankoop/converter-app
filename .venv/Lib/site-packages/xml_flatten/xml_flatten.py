import re
xml_flat=[]

def rem_nm_spc(tag_w_nsp):
    m=re.search(r"\{(.*?)\}",tag_w_nsp)
    tag=tag_w_nsp.replace(m.group(0),'')
    return(tag)


def rec(i,x,xpath):
    global xml_flat
    #print("-" * x ,xpath, dict([(i.tag,i.text.replace("\n","").replace("\r","").replace("\t",""))]), i.attrib if(len(i.attrib)>0) else "")
    try:
        xml_flat.append([xpath, dict([(rem_nm_spc(i.tag),i.text.replace("\n","").replace("\r","").replace("\t",""))]), i.attrib if(len(i.attrib)>0) else ""])
    except:
        xml_flat.append([xpath, dict([(i.tag,i.text.replace("\n","").replace("\r","").replace("\t",""))]), i.attrib if(len(i.attrib)>0) else ""])
    x=x+len(i)
    try:
        xpath = xpath+">"+rem_nm_spc(i.tag)
    except:
        xpath = xpath+">"+i.tag
    for j in i:
        if len(j)>0:
            rec(j,x,xpath)
        else:
            #print("-" * x , xpath,dict([(j.tag,j.text)]),j.attrib if(len(j.attrib)>0) else "")
            try:
                xml_flat.append([xpath,dict([(rem_nm_spc(j.tag),j.text)]),j.attrib if(len(j.attrib)>0) else ""])
            except:
                xml_flat.append([xpath,dict([(j.tag,j.text)]),j.attrib if(len(j.attrib)>0) else ""])
    return()