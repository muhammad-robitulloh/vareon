import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DialogFooter } from '@/components/ui/dialog';

interface AddModelFormProps {
  onAddModel: (modelData: any) => void;
  providers: any[]; // Assuming providers is an array of objects with at least 'id' and 'name'
}

const AddModelForm: React.FC<AddModelFormProps> = ({ onAddModel, providers }) => {
  const [modelName, setModelName] = useState('');
  const [providerId, setProviderId] = useState('');
  const [modelType, setModelType] = useState('');
  const [maxTokens, setMaxTokens] = useState<number | ''>('');
  const [costPerToken, setCostPerToken] = useState<number | ''>('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!modelName || !providerId || !modelType) {
      alert('Please fill in all required fields.');
      return;
    }
    onAddModel({ modelName, providerId, modelType, maxTokens, costPerToken });
    // Clear form
    setModelName('');
    setProviderId('');
    setModelType('');
    setMaxTokens('');
    setCostPerToken('');
  };

  return (
    <form onSubmit={handleSubmit} className="grid gap-4 py-4">
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="modelName" className="text-right">
          Model Name
        </Label>
        <Input
          id="modelName"
          value={modelName}
          onChange={(e) => setModelName(e.target.value)}
          className="col-span-3"
          required
        />
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="provider" className="text-right">
          Provider
        </Label>
        <Select value={providerId} onValueChange={setProviderId} required>
          <SelectTrigger className="col-span-3">
            <SelectValue placeholder="Select a provider" />
          </SelectTrigger>
          <SelectContent>
            {providers.map((provider) => (
              <SelectItem key={provider.id} value={provider.id}>
                {provider.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="modelType" className="text-right">
          Model Type
        </Label>
        <Select value={modelType} onValueChange={setModelType} required>
          <SelectTrigger className="col-span-3">
            <SelectValue placeholder="Select model type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="chat">Chat</SelectItem>
            <SelectItem value="completion">Completion</SelectItem>
            <SelectItem value="embedding">Embedding</SelectItem>
            {/* Add other model types as needed */}
          </SelectContent>
        </Select>
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="maxTokens" className="text-right">
          Max Tokens
        </Label>
        <Input
          id="maxTokens"
          type="number"
          value={maxTokens}
          onChange={(e) => setMaxTokens(e.target.value === '' ? '' : Number(e.target.value))}
          className="col-span-3"
        />
      </div>
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="costPerToken" className="text-right">
          Cost/Token
        </Label>
        <Input
          id="costPerToken"
          type="number"
          step="0.0000001"
          value={costPerToken}
          onChange={(e) => setCostPerToken(e.target.value === '' ? '' : Number(e.target.value))}
          className="col-span-3"
        />
      </div>
      <DialogFooter>
        <Button type="submit">Add Model</Button>
      </DialogFooter>
    </form>
  );
};

export default AddModelForm;
