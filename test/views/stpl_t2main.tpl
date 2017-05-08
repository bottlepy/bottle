%def test(var):
+{{var}}+
%end
%rebase('stpl_t2base', test=test)
%test('main')
!{{content}}!
%_ = include('stpl_t2inc', test=test)
%_['test2']('main')
