 SELECT
            c.CustomerID,
            c.FirstName || ' ' || c.LastName AS CustomerName,
			round(avg(creditscore)) as creditscores,
            COALESCE(SUM(l.loanamount), 0) AS TotalBorrowed,
            COALESCE(SUM(t.investmentamount), 0) AS TotalInvested
        FROM
            Customers c
        LEFT JOIN CreditScores cs ON c.CustomerID = cs.CustomerID
        LEFT JOIN Loans l ON l.BorrowerID = c.CustomerID
        LEFT JOIN loaninvestments t ON t.LenderID = c.CustomerID
        GROUP BY
            c.CustomerID, c.FirstName, c.LastName
        ORDER BY
            c.CustomerID;

SELECT TO_CHAR(startdate, 'YYYY-MM') AS Month, sum(loanamount) AS LoanedAmount
    FROM Loans
    GROUP BY TO_CHAR(startdate, 'YYYY-MM')
    ORDER BY Month;

SELECT TO_CHAR(repaymentdate, 'YYYY-MM-DD') AS Month, sum(repaymentamount) AS RepaidAmount
    FROM Loanrepayments
    GROUP BY TO_CHAR(repaymentdate, 'YYYY-MM-DD')
    LIMIT 7;

Select TO_CHAR(transactiondate, 'YYYY-MM') as month, count(transactionid) from transactions
GROUP BY TO_CHAR(transactiondate, 'YYYY-MM')
order by month;


SELECT Role, COUNT(*) AS CustomerCount
FROM Customers
GROUP BY Role;

SELECT LoanStatus, COUNT(*) AS LoanCount, SUM(LoanAmount) AS TotalAmount
FROM Loans
GROUP BY LoanStatus;

SELECT 
    l.LoanID, 
    l.LoanAmount, 
    SUM(lr.RepaymentAmount) AS TotalRepaid, 
    l.LoanAmount - SUM(lr.RepaymentAmount) AS OutstandingBalance
FROM Loans l
LEFT JOIN LoanRepayments lr ON l.LoanID = lr.LoanID
GROUP BY l.LoanID, l.LoanAmount
HAVING l.LoanAmount - SUM(lr.RepaymentAmount) > 0;

SELECT 
    CASE 
        WHEN CreditScore BETWEEN 300 AND 579 THEN 'Poor'
        WHEN CreditScore BETWEEN 580 AND 669 THEN 'Fair'
        WHEN CreditScore BETWEEN 670 AND 739 THEN 'Good'
        WHEN CreditScore BETWEEN 740 AND 799 THEN 'Very Good'
        ELSE 'Excellent'
    END AS ScoreRange,
    COUNT(*) AS CustomerCount
FROM CreditScores
GROUP BY ScoreRange
ORDER BY ScoreRange;

SELECT 
    c.CustomerID, 
    c.FirstName || ' ' || c.LastName AS CustomerName, 
    SUM(l.LoanAmount) AS TotalBorrowed
FROM Customers c
JOIN Loans l ON c.CustomerID = l.BorrowerID
GROUP BY c.CustomerID, c.FirstName, c.LastName
ORDER BY TotalBorrowed DESC
LIMIT 5;

SELECT 
    c.CustomerID, 
    c.FirstName || ' ' || c.LastName AS CustomerName, 
    SUM(li.InvestmentAmount) AS TotalInvested
FROM Customers c
JOIN LoanInvestments li ON c.CustomerID = li.LenderID
GROUP BY c.CustomerID, c.FirstName, c.LastName
ORDER BY TotalInvested DESC
LIMIT 5;
