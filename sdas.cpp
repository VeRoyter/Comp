#include <iostream>
#include <string>
#include <cmath>
using namespace std;

int calculate(int val1, int val2, bool add) {
    int localRes;
    int temp;
    if (add == true) {
    localRes = (val1 + val2);
} else {
    localRes = (val1 - val2);
}
    return localRes;
}

int main()
{
    int num1, num2, total;
    double pi, radius;
    bool isValid, isDone;
    string strA, strB, strFull;
    
    num1 = 10;
    num2 = 5;
    isValid = true;
    total = calculate(num1, num2, isValid);
    cout << total << endl;
    strA = "Hello";
    strB = "World";
    strFull = ((strA + " ") + strB);
    cout << strFull << endl;
    if (total > 10) cout << "Result is greater than 10" << endl; else cout << "Result is small" << endl;
    while (num1 > 0) {
    num1 = (num1 - 5);
    cout << num1 << endl;
}
}