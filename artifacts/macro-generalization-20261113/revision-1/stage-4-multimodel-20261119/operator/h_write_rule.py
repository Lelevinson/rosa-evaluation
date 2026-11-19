"""Frozen-in-advance descriptive H-write rule for the exploratory extension."""
ALLOWED={'Support','Against','Uninformative'}
def classify(p_write,m_write,p_other,m_other,*,complete=True):
    if not complete:return 'Uninformative'
    for value,limit in [(p_write,8),(m_write,8),(p_other,28),(m_other,28)]:
        if type(value) is not int or not 0<=value<=limit:raise ValueError('invalid_pass_count')
    if p_write in (0,8) or m_write in (0,8):return 'Uninformative'
    if m_write<=p_write:return 'Against'
    return 'Support' if m_write-p_write>m_other-p_other else 'Uninformative'
def overall(statuses):
    if len(statuses)!=3 or any(s not in ALLOWED for s in statuses):raise ValueError('fixed_three_model_sample_required')
    if statuses.count('Support')>=2:return 'Support'
    if statuses.count('Against')>=2:return 'Against'
    return 'Uninformative'
def self_check():
    fixtures=[
      ((2,6,24,24),True,'Support'),((2,8,24,24),True,'Uninformative'),
      ((0,4,20,20),True,'Uninformative'),((4,0,20,20),True,'Uninformative'),
      ((8,4,20,20),True,'Uninformative'),((4,4,24,24),True,'Against'),
      ((5,3,24,24),True,'Against'),((2,4,24,26),True,'Uninformative'),
      ((2,3,24,26),True,'Uninformative'),((2,3,26,20),True,'Support'),
      ((2,6,24,24),False,'Uninformative')]
    for counts,complete,expected in fixtures:assert classify(*counts,complete=complete)==expected
    for values,expected in [
      (['Support','Support','Uninformative'],'Support'),
      (['Against','Uninformative','Against'],'Against'),
      (['Support','Against','Uninformative'],'Uninformative'),
      (['Uninformative']*3,'Uninformative')]:assert overall(values)==expected
    return {'pass':True,'synthetic_checks':len(fixtures)+4,'model_requests':0,
            'floor_override_tested':True,'raw_difference_not_rate_difference':True,
            'support_can_coexist_with_worse_overall_accuracy':True,
            'actual_backend_results_evaluated':False}
if __name__=='__main__':
    import json
    print(json.dumps(self_check()))
