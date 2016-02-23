int factorial(int n)
{
	register int f;
	f = 1;
	while(n)
		f *= n--;
	return f;
}
