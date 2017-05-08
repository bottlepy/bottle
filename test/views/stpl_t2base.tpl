%test('base')
{{base}}\\
%_ = include('stpl_t2inc', test=test)
%_['test2']('base')
