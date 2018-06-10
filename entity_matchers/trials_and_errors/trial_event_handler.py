import os
sys.path.append('..')
import PostgreSQLHanddler

p = PostgreSQLHandler()
res = p.execute("""select * from tutorials""")
for t in res:
    for f in t:
        print('%s ' % f, end='')
    print()