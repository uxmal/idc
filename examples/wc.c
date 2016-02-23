/* Copyright (c) 2007 the authors listed at the following URL, and/or
the authors of referenced articles or incorporated external code:
http://en.literateprograms.org/Word_count_(C)?action=history&offset=20070621055849

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Retrieved from: http://en.literateprograms.org/Word_count_(C)?oldid=10559
*/

#include<stdio.h>
#include<ctype.h>

enum {OPT_C=4, OPT_W=2, OPT_L=1};

int print(const char *fname, int opt, int chars, int words, int lines)
{
	if(opt&OPT_L) printf("% 8d", lines);
	if(opt&OPT_W) printf("% 8d", words);
	if(opt&OPT_C) printf("% 8d", chars);


	if(fname[0]!='-') printf(" %s", fname);

	putchar('\n');

	return 0;
}


int wc(const char *fname, int opt, int *tot_chars, int *tot_words, int *tot_lines)
{
	int ch;
	int chars=0;
	int words=0;
	int lines=0;
	int sp=1;
	FILE *fp;


	if(fname[0]!='-') fp=fopen(fname, "r");
	else fp=stdin;
	if(!fp) return -1;

	while((ch=getc(fp))!=EOF) {

		++chars;

		if(isspace(ch)) sp=1;
		else if(sp) {
			++words;
			sp=0;
		}

		if(ch=='\n') ++lines;
	}


	print(fname, opt, chars, words, lines);

	if(fname[0]!='-') fclose(fp);

	*tot_chars+=chars;
	*tot_words+=words;
	*tot_lines+=lines;

	return 0;
}


int main(int argc, char *argv[])
{
	int chars=0;
	int words=0;
	int lines=0;
	int nfiles=0;
	int opt=0;
	int n;

	while((++argv)[0] && argv[0][0]=='-') {

		n=1;
		while(argv[0][n]) {
			switch(argv[0][n++]) {
			case 'c': opt|=OPT_C; break;
			case 'w': opt|=OPT_W; break;
			case 'l': opt|=OPT_L; break;
			default:
				fprintf(stderr, "Unknown option %c\n", argv[0][n-1]);
				fprintf(stderr, "Usage: wc [-cwl] [<filename>*]\n");
				return -1;
			}
		}
	}

	if(!opt) opt=OPT_L|OPT_W|OPT_C;

	while(argv[0]) {
		++nfiles;
		if(wc(*argv, opt, &chars, &words, &lines)==-1) {
			perror(*argv);
			return 1;
		}
		++argv;
	}


	if(nfiles==0) wc("-", opt, &chars, &words, &lines);

	else if(nfiles>1) print("total", opt, chars, words, lines);

	return 0;
}



