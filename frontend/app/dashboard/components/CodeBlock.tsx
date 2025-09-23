'use client';

import React from 'react';
// @ts-ignore
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
// @ts-ignore
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import { Copy, Check } from 'lucide-react';
import { Button } from "@/app/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";

interface CodeBlockProps {
  language: string;
  value: string;
  framework?: string;
}

const CodeBlock = ({ language, value, framework }: CodeBlockProps) => {
  const [copied, setCopied] = React.useState(false);
  
  // Determine the language for syntax highlighting
  const getLanguage = () => {
    if (language) return language.toLowerCase();
    // Try to detect language from code content
    if (value.includes('def ') && value.includes('import')) return 'python';
    if (value.includes('function') && value.includes('const')) return 'javascript';
    if (value.includes('public class') || value.includes('public static')) return 'java';
    return 'text';
  };
  
  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const detectedLanguage = getLanguage();
  const frameworkName = framework || 
    (detectedLanguage === 'python' ? 'Python' : 
     detectedLanguage === 'javascript' ? 'JavaScript' : 
     detectedLanguage === 'java' ? 'Java' : 'Code');

  return (
    <Card className="bg-white/40 backdrop-blur-lg border border-white/20 shadow-lg overflow-hidden">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-medium flex items-center gap-2">
            <span className="font-mono text-sm">{frameworkName} Implementation</span>
            <Badge variant="secondary" className="text-xs">
              {detectedLanguage}
            </Badge>
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopy}
            className="h-8 w-8 p-0"
          >
            {copied ? (
              <Check className="h-4 w-4 text-green-500" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="rounded-md overflow-hidden">
          <SyntaxHighlighter 
            style={oneDark} 
            language={detectedLanguage} 
            PreTag="div"
            className="text-xs !p-4 !m-0"
            showLineNumbers
          >
            {value || '// No code generated'}
          </SyntaxHighlighter>
        </div>
      </CardContent>
    </Card>
  );
};

export default CodeBlock;