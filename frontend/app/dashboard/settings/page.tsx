'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Button } from "@/app/components/ui/button";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
import { Textarea } from "@/app/components/ui/textarea";
import { 
  Settings, 
  Save,
  RotateCcw,
  Database,
  Shield,
  Bell
} from 'lucide-react';
import { useState } from 'react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    defaultModel: 'gemini-2.0-flash',
    defaultFramework: 'playwright',
    defaultBrowser: 'chrome',
    maxParallelAgents: '5',
    customExecutablePath: '',
    notificationEmail: '',
    apiKey: '',
    customPrompt: ''
  });

  const handleSave = () => {
    // In a real app, this would save to a backend or local storage
    console.log('Saving settings:', settings);
    alert('Settings saved successfully!');
  };

  const handleReset = () => {
    setSettings({
      defaultModel: 'gemini-2.0-flash',
      defaultFramework: 'playwright',
      defaultBrowser: 'chrome',
      maxParallelAgents: '5',
      customExecutablePath: '',
      notificationEmail: '',
      apiKey: '',
      customPrompt: ''
    });
  };

  const handleChange = (field: string, value: string) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Settings className="h-8 w-8 text-primary" />
          Settings
        </h1>
        <p className="text-muted-foreground">
          Configure your SDET-GENIE preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                General
              </CardTitle>
            </CardHeader>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security
              </CardTitle>
            </CardHeader>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notifications
              </CardTitle>
            </CardHeader>
          </Card>
        </div>
        
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>
                Configure default options for your test executions
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="defaultModel">Default AI Model</Label>
                  <Input
                    id="defaultModel"
                    value={settings.defaultModel}
                    onChange={(e) => handleChange('defaultModel', e.target.value)}
                    placeholder="Enter model name"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="defaultFramework">Default Framework</Label>
                  <Input
                    id="defaultFramework"
                    value={settings.defaultFramework}
                    onChange={(e) => handleChange('defaultFramework', e.target.value)}
                    placeholder="Enter framework"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="defaultBrowser">Default Browser</Label>
                  <Input
                    id="defaultBrowser"
                    value={settings.defaultBrowser}
                    onChange={(e) => handleChange('defaultBrowser', e.target.value)}
                    placeholder="Enter browser name"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="maxParallelAgents">Max Parallel Agents</Label>
                  <Input
                    id="maxParallelAgents"
                    type="number"
                    value={settings.maxParallelAgents}
                    onChange={(e) => handleChange('maxParallelAgents', e.target.value)}
                    placeholder="Enter number"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="customExecutablePath">Custom Browser Executable Path</Label>
                <Input
                  id="customExecutablePath"
                  value={settings.customExecutablePath}
                  onChange={(e) => handleChange('customExecutablePath', e.target.value)}
                  placeholder="Enter full path to browser executable"
                />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>
                Manage your API keys and authentication
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="apiKey">API Key</Label>
                <Input
                  id="apiKey"
                  type="password"
                  value={settings.apiKey}
                  onChange={(e) => handleChange('apiKey', e.target.value)}
                  placeholder="Enter your API key"
                />
                <p className="text-sm text-muted-foreground">
                  Your API key is used to authenticate with external services
                </p>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Notification Settings</CardTitle>
              <CardDescription>
                Configure how you receive notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="notificationEmail">Notification Email</Label>
                <Input
                  id="notificationEmail"
                  type="email"
                  value={settings.notificationEmail}
                  onChange={(e) => handleChange('notificationEmail', e.target.value)}
                  placeholder="Enter your email address"
                />
                <p className="text-sm text-muted-foreground">
                  Receive email notifications for completed executions
                </p>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Custom Prompt</CardTitle>
              <CardDescription>
                Add a custom prompt that will be appended to all AI requests
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Textarea
                  value={settings.customPrompt}
                  onChange={(e) => handleChange('customPrompt', e.target.value)}
                  placeholder="Enter custom prompt instructions..."
                  rows={6}
                />
                <p className="text-sm text-muted-foreground">
                  This prompt will be added to enhance all AI-generated content
                </p>
              </div>
            </CardContent>
          </Card>
          
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={handleReset} className="flex items-center gap-2">
              <RotateCcw className="h-4 w-4" />
              Reset to Defaults
            </Button>
            <Button onClick={handleSave} className="flex items-center gap-2">
              <Save className="h-4 w-4" />
              Save Settings
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}