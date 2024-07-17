select * from accounts a left join transactions b
on a.id = b.account_id
    where 
    a.batchentrydate > '2024-07-07'
    AND
    a.batchentrydate < '2024-07-17'
    AND
    trim(a.ACCOUNTNO) IN (
    '12345678901',
'99999999999',
'09898987666' )