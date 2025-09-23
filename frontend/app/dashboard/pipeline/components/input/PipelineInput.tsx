import React, { useState, useEffect } from 'react';
import { Button } from "@/app/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Textarea } from "@/app/components/ui/textarea";
import { Label } from "@/app/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/app/components/ui/select";
import { Input } from "@/app/components/ui/input";
import { Badge } from "@/app/components/ui/badge";
import { Separator } from "@/app/components/ui/separator";
import { 
  Play, 
  Loader2, 
  Settings, 
  Zap, 
  Eye, 
  Monitor,
  Smartphone,
  Tablet,
  Laptop,
  Bot,
  Sparkles,
  Gauge,
  Chrome,
  Globe,
  // Let's try to import Chromium and see if it exists
  Chromium
} from 'lucide-react';

// Define prop types
interface PipelineInputProps {
  rawStory?: string;
  setRawStory?: (value: string) => void;
  context?: string;
  setContext?: (value: string) => void;
  selectedFramework?: string;
  setSelectedFramework?: (value: string) => void;
  provider?: string;
  setProvider?: (value: string) => void;
  model?: string;
  setModel?: (value: string) => void;
  isRunning?: boolean;
  onStartPipeline?: () => void;
  selectedBrowser?: string;
  setSelectedBrowser?: (value: string) => void;
  selectedResolution?: [number, number];
  setSelectedResolution?: (value: [number, number]) => void;
  customExecutablePath?: string;
  setCustomExecutablePath?: (value: string) => void;
  visionEnabled?: boolean;
  setVisionEnabled?: (value: boolean) => void;
  cdpPort?: string;
  setCdpPort?: (value: string) => void;
}

const PipelineInput: React.FC<PipelineInputProps> = (props) => {
  // Destructure props with proper defaults
  const {
    rawStory = '',
    setRawStory = () => {},
    context = '',
    setContext = () => {},
    selectedFramework = '',
    setSelectedFramework = () => {},
    provider = 'Google',
    setProvider = () => {},
    model = 'gemini-2.0-flash',
    setModel = () => {},
    isRunning = false,
    onStartPipeline = () => {},
    selectedBrowser = 'chrome',
    setSelectedBrowser = () => {},
    selectedResolution = [1920, 1080],
    setSelectedResolution = () => {},
    customExecutablePath = '',
    setCustomExecutablePath = () => {},
    visionEnabled = true,
    setVisionEnabled = () => {},
    cdpPort = '',
    setCdpPort = () => {}
  } = props;

  const [availableBrowsers, setAvailableBrowsers] = useState({});
  const [supportedResolutions, setSupportedResolutions] = useState([]);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);

  const FRAMEWORKS = [
    { 
      value: "Selenium + PyTest BDD (Python)", 
      label: "Selenium + PyTest BDD", 
      tech: "Python",
      icon: "🐍",
      description: "Robust automation with BDD approach"
    },
    { 
      value: "Playwright (Python)", 
      label: "Playwright", 
      tech: "Python",
      icon: "🎭",
      description: "Modern automation with cross-browser support"
    },
    { 
      value: "Cypress (JavaScript)", 
      label: "Cypress", 
      tech: "JavaScript",
      icon: "🌲",
      description: "Fast, reliable testing for modern web apps"
    },
    { 
      value: "Robot Framework", 
      label: "Robot Framework", 
      tech: "Keywords",
      icon: "🤖",
      description: "Keyword-driven test automation"
    },
    { 
      value: "Selenium + Cucumber (Java)", 
      label: "Selenium + Cucumber", 
      tech: "Java",
      icon: "☕",
      description: "Enterprise-grade automation with BDD"
    }
  ];

  const MODELS = [
    { 
      value: "gemini-2.0-flash", 
      label: "Gemini 2.0 Flash", 
      provider: "Google",
      tier: "Latest",
      speed: "⚡ Fast"
    },
    { 
      value: "gemini-1.5-pro", 
      label: "Gemini 1.5 Pro", 
      provider: "Google",
      tier: "Pro",
      speed: "🔥 Balanced"
    },
    { 
      value: "gpt-4o", 
      label: "GPT-4O", 
      provider: "OpenAI",
      tier: "Premium",
      speed: "💎 Advanced"
    },
    { 
      value: "claude-3-5-sonnet", 
      label: "Claude 3.5 Sonnet", 
      provider: "Anthropic",
      tier: "Pro",
      speed: "🎯 Precise"
    },
    { 
      value: "llama-3.1-70b", 
      label: "Llama 3.1 70B", 
      provider: "Groq",
      tier: "Open Source",
      speed: "🚀 Ultra Fast"
    }
  ];

  const PROVIDERS = [
    { value: "Google", label: "Google", color: "bg-blue-500", icon: "🔵" },
    { value: "OpenAI", label: "OpenAI", color: "bg-green-500", icon: "🟢" },
    { value: "Anthropic", label: "Anthropic", color: "bg-orange-500", icon: "🟠" },
    { value: "Groq", label: "Groq", color: "bg-purple-500", icon: "🟣" }
  ];

  const RESOLUTION_PRESETS = [
    { name: "Desktop FHD", width: 1920, height: 1080, icon: <Monitor className="h-4 w-4" /> },
    { name: "Desktop HD", width: 1366, height: 768, icon: <Monitor className="h-4 w-4" /> },
    { name: "Laptop", width: 1440, height: 900, icon: <Laptop className="h-4 w-4" /> },
    { name: "Tablet", width: 1024, height: 768, icon: <Tablet className="h-4 w-4" /> },
    { name: "Mobile", width: 375, height: 812, icon: <Smartphone className="h-4 w-4" /> },
    { name: "4K UHD", width: 3840, height: 2160, icon: <Monitor className="h-4 w-4" /> }
  ];

  const getSelectedFramework = () => {
    return FRAMEWORKS.find(f => f.value === selectedFramework);
  };

  const getSelectedModel = () => {
    return MODELS.find(m => m.value === model);
  };

  const getSelectedProvider = () => {
    return PROVIDERS.find(p => p.value === provider);
  };

  return (
    <Card className="relative overflow-hidden bg-gradient-to-br from-white via-blue-50/30 to-indigo-50/40 dark:from-gray-900 dark:via-gray-800/50 dark:to-gray-900 backdrop-blur-xl border border-white/20 dark:border-gray-700/30 shadow-2xl">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-teal-500/5 animate-pulse" />
      
      <CardHeader className="relative space-y-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg">
                <Zap className="h-5 w-5" />
              </div>
              <CardTitle className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
                Pipeline Configuration
              </CardTitle>
            </div>
            <CardDescription className="text-lg">
              Configure your automated QA pipeline with advanced settings
            </CardDescription>
          </div>
          <Badge variant="secondary" className="bg-green-100 text-green-800 border-green-200">
            <Sparkles className="h-3 w-3 mr-1" />
            AI Powered
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="relative space-y-6">
        {/* User Story Input */}
        <div className="space-y-3">
          <Label htmlFor="user-story" className="text-base font-semibold flex items-center gap-2">
            <Bot className="h-4 w-4 text-blue-500" />
            User Story
          </Label>
          <div className="relative">
            <Textarea
              id="user-story"
              value={rawStory}
              onChange={(e) => setRawStory(e.target.value)}
              placeholder="Describe your user story or paste a Jira ticket (e.g., PROJECT-123)..."
              className="min-h-[120px] resize-none bg-white/70 dark:bg-gray-800/70 border-2 border-gray-200 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 rounded-xl shadow-inner transition-all duration-200"
              disabled={isRunning}
            />
            <div className="absolute bottom-3 right-3">
              <Badge variant="outline" className="text-xs">
                {rawStory.length}/2000
              </Badge>
            </div>
          </div>
        </div>

        {/* Context Input */}
        <div className="space-y-3">
          <Label htmlFor="context" className="text-base font-semibold">
            Additional Context <span className="text-gray-500 font-normal">(Optional)</span>
          </Label>
          <Textarea
            id="context"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Provide any additional context, requirements, or constraints..."
            className="min-h-[80px] resize-none bg-white/70 dark:bg-gray-800/70 border-2 border-gray-200 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 rounded-xl shadow-inner transition-all duration-200"
            disabled={isRunning}
          />
        </div>

        <Separator className="my-6" />

        {/* Framework Selection */}
        <div className="space-y-3">
          <Label htmlFor="framework" className="text-base font-semibold">
            Testing Framework
          </Label>
          <Select value={selectedFramework} onValueChange={setSelectedFramework} disabled={isRunning}>
            <SelectTrigger className="h-14 bg-white/70 dark:bg-gray-800/70 border-2 border-gray-200 dark:border-gray-600 rounded-xl">
              <SelectValue placeholder="Choose your preferred testing framework">
                {getSelectedFramework() && (
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{getSelectedFramework()?.icon}</span>
                    <div className="text-left">
                      <div className="font-semibold">{getSelectedFramework()?.label}</div>
                      <div className="text-xs text-gray-500">{getSelectedFramework()?.description}</div>
                    </div>
                    <Badge variant="secondary" className="ml-auto">
                      {getSelectedFramework()?.tech}
                    </Badge>
                  </div>
                )}
              </SelectValue>
            </SelectTrigger>
            <SelectContent className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg border border-gray-200 dark:border-gray-600 rounded-xl">
              {FRAMEWORKS.map((framework) => (
                <SelectItem key={framework.value} value={framework.value} className="h-14 rounded-lg">
                  <div className="flex items-center gap-3 w-full">
                    <span className="text-lg">{framework.icon}</span>
                    <div className="flex-1">
                      <div className="font-semibold">{framework.label}</div>
                      <div className="text-xs text-gray-500">{framework.description}</div>
                    </div>
                    <Badge variant="outline" className="ml-2">
                      {framework.tech}
                    </Badge>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* AI Model Configuration */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-3">
            <Label className="text-base font-semibold">AI Provider</Label>
            <Select value={provider} onValueChange={setProvider} disabled={isRunning}>
              <SelectTrigger className="h-12 bg-white/70 dark:bg-gray-800/70 border-2 border-gray-200 dark:border-gray-600 rounded-xl">
                <SelectValue>
                  {getSelectedProvider() && (
                    <div className="flex items-center gap-2">
                      <span>{getSelectedProvider()?.icon}</span>
                      <span className="font-semibold">{getSelectedProvider()?.label}</span>
                    </div>
                  )}
                </SelectValue>
              </SelectTrigger>
              <SelectContent className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg">
                {PROVIDERS.map((prov) => (
                  <SelectItem key={prov.value} value={prov.value}>
                    <div className="flex items-center gap-2">
                      <span>{prov.icon}</span>
                      <span>{prov.label}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-3">
            <Label className="text-base font-semibold">AI Model</Label>
            <Select value={model} onValueChange={setModel} disabled={isRunning}>
              <SelectTrigger className="h-12 bg-white/70 dark:bg-gray-800/70 border-2 border-gray-200 dark:border-gray-600 rounded-xl">
                <SelectValue>
                  {getSelectedModel() && (
                    <div className="flex items-center justify-between w-full">
                      <span className="font-semibold">{getSelectedModel()?.label}</span>
                      <Badge variant="outline" className="text-xs">
                        {getSelectedModel()?.tier}
                      </Badge>
                    </div>
                  )}
                </SelectValue>
              </SelectTrigger>
              <SelectContent className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg">
                {MODELS.map((mod) => (
                  <SelectItem key={mod.value} value={mod.value}>
                    <div className="flex items-center justify-between w-full">
                      <div>
                        <div className="font-semibold">{mod.label}</div>
                        <div className="text-xs text-gray-500">{mod.speed}</div>
                      </div>
                      <div className="text-right">
                        <Badge variant="outline" className="text-xs">
                          {mod.tier}
                        </Badge>
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <Separator className="my-6" />

        {/* Browser Configuration */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label className="text-base font-semibold flex items-center gap-2">
              <Monitor className="h-4 w-4 text-blue-500" />
              Browser Configuration
            </Label>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-3">
              <Label>Browser</Label>
              <Select value={selectedBrowser} onValueChange={setSelectedBrowser} disabled={isRunning}>
                <SelectTrigger className="h-12 bg-white/70 dark:bg-gray-800/70 border-2 border-gray-200 dark:border-gray-600 rounded-xl">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg">
                  <SelectItem value="chrome">
                    <div className="flex items-center gap-2">
                      <Chrome className="h-4 w-4" />
                      Google Chrome
                    </div>
                  </SelectItem>
                  <SelectItem value="firefox">
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4" />
                      Mozilla Firefox
                    </div>
                  </SelectItem>
                  <SelectItem value="edge">
                    <div className="flex items-center gap-2">
                      <Chromium className="h-4 w-4" />
                      Microsoft Edge
                    </div>
                  </SelectItem>
                  <SelectItem value="safari">
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4" />
                      Safari
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-3">
              <Label>Resolution</Label>
              <Select 
                value={`${selectedResolution[0]}x${selectedResolution[1]}`} 
                onValueChange={(value) => {
                  const [width, height] = value.split('x').map(Number);
                  setSelectedResolution([width, height]);
                }} 
                disabled={isRunning}
              >
                <SelectTrigger className="h-12 bg-white/70 dark:bg-gray-800/70 border-2 border-gray-200 dark:border-gray-600 rounded-xl">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg">
                  {RESOLUTION_PRESETS.map((res) => (
                    <SelectItem key={`${res.width}x${res.height}`} value={`${res.width}x${res.height}`}>
                      <div className="flex items-center gap-2">
                        {res.icon}
                        <span>{res.name} ({res.width}×{res.height})</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Advanced Settings Toggle */}
        <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <Settings className="h-4 w-4 text-gray-500" />
            <span className="font-semibold">Advanced Settings</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
          >
            {showAdvancedSettings ? 'Hide' : 'Show'}
          </Button>
        </div>

        {/* Advanced Settings Panel */}
        {showAdvancedSettings && (
          <div className="space-y-4 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900 rounded-xl border border-blue-200 dark:border-gray-600">
            {/* Vision Toggle */}
            <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-600 text-white">
                  <Eye className="h-4 w-4" />
                </div>
                <div>
                  <Label className="text-base font-semibold">Vision Intelligence</Label>
                  <p className="text-sm text-gray-500">Enable AI visual understanding</p>
                </div>
              </div>
              <div className="relative">
                <input
                  type="checkbox"
                  id="vision-enabled"
                  checked={visionEnabled}
                  onChange={(e) => setVisionEnabled(e.target.checked)}
                  disabled={isRunning}
                  className="sr-only"
                />
                <div
                  onClick={() => !isRunning && setVisionEnabled(!visionEnabled)}
                  className={`w-14 h-8 rounded-full cursor-pointer transition-all duration-300 ${
                    visionEnabled 
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-600 shadow-lg' 
                      : 'bg-gray-300 dark:bg-gray-600'
                  } ${isRunning ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <div
                    className={`w-6 h-6 bg-white rounded-full shadow-md transition-transform duration-300 mt-1 ml-1 ${
                      visionEnabled ? 'transform translate-x-6' : ''
                    }`}
                  />
                </div>
              </div>
            </div>

            {/* Custom Executable Path */}
            <div className="space-y-3">
              <Label className="text-base font-semibold">Custom Browser Path</Label>
              <Input
                value={customExecutablePath}
                onChange={(e) => setCustomExecutablePath(e.target.value)}
                placeholder="/path/to/browser/executable (optional)"
                className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 rounded-lg"
                disabled={isRunning}
              />
            </div>

            {/* CDP Port */}
            <div className="space-y-3">
              <Label className="text-base font-semibold">Chrome DevTools Port</Label>
              <Input
                type="number"
                value={cdpPort}
                onChange={(e) => setCdpPort(e.target.value)}
                placeholder="9222 (default)"
                className="bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 rounded-lg"
                disabled={isRunning}
              />
            </div>
          </div>
        )}

        {/* Start Pipeline Button */}
        <Button 
          onClick={onStartPipeline} 
          disabled={isRunning || !rawStory || !selectedFramework}
          className="w-full h-14 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-lg rounded-xl shadow-xl transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
        >
          {isRunning ? (
            <>
              <Loader2 className="mr-3 h-5 w-5 animate-spin" />
              Pipeline Running...
            </>
          ) : (
            <>
              <Play className="mr-3 h-5 w-5" />
              Start AI Pipeline
              <Gauge className="ml-3 h-5 w-5" />
            </>
          )}
        </Button>

        {/* Pipeline Status Indicators */}
        {isRunning && (
          <div className="flex items-center justify-center gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
            </div>
            <span className="text-blue-700 dark:text-blue-300 font-medium">
              AI is analyzing your requirements...
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PipelineInput;