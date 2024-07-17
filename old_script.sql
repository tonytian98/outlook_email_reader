select * 
from accounts a 
left join transactions b 
on a.id = b.account_id
where 

a.batchentrydate > '2024-04-01'
AND
a.batchentrydate < '2024-04-07'
AND
trim(a.ACCOUNTNO) IN (
    12345678901,
    99999999999,
    09898987666
)