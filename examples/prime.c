int prime(int n)
{
	register int i;
	if(n == 1 || n == 2)
		return 1;
	if(!(n % 2))
		return 0;
	for(i = 3; i  < n/2; ++i)
		if(!(n % i))
			return 0;
	return 1;
}
