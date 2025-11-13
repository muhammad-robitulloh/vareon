import React, { useState } from 'react';
import { Button, Select, SelectContent, SelectItem, SelectTrigger, SelectValue, Input } from '@/components/ui';
import { Plus, Trash2 } from 'lucide-react';

interface Condition {
  id: string;
  fact: string;
  operator: string;
  value: string;
}

interface ConditionGroup {
  id: string;
  combinator: 'and' | 'or';
  rules: (Condition | ConditionGroup)[];
}

type Rule = Condition | ConditionGroup;

interface ConditionBuilderProps {
  root: ConditionGroup;
  setRoot: React.Dispatch<React.SetStateAction<ConditionGroup>>;
}

const ConditionBuilder: React.FC<ConditionBuilderProps> = ({ root, setRoot }) => {

  const handleAddCondition = (groupId: string) => {
    const newCondition: Condition = {
      id: Date.now().toString(),
      fact: 'intent',
      operator: 'equals',
      value: '',
    };

    const addConditionRecursively = (group: ConditionGroup): ConditionGroup => {
      if (group.id === groupId) {
        return { ...group, rules: [...group.rules, newCondition] };
      }
      return {
        ...group,
        rules: group.rules.map(rule => {
          if ('combinator' in rule) {
            return addConditionRecursively(rule as ConditionGroup);
          }
          return rule;
        }),
      };
    };

    setRoot(prevRoot => addConditionRecursively(prevRoot));
  };

  const handleRemoveCondition = (conditionId: string) => {
    const removeConditionRecursively = (group: ConditionGroup): ConditionGroup => {
      return {
        ...group,
        rules: group.rules.filter(rule => rule.id !== conditionId).map(rule => {
          if ('combinator' in rule) {
            return removeConditionRecursively(rule as ConditionGroup);
          }
          return rule;
        }),
      };
    };
    setRoot(prevRoot => removeConditionRecursively(prevRoot));
  };

  const handleUpdateCondition = (conditionId: string, newValues: Partial<Condition>) => {
    const updateConditionRecursively = (group: ConditionGroup): ConditionGroup => {
      return {
        ...group,
        rules: group.rules.map(rule => {
          if (rule.id === conditionId) {
            return { ...rule, ...newValues };
          }
          if ('combinator' in rule) {
            return updateConditionRecursively(rule as ConditionGroup);
          }
          return rule;
        }),
      };
    };
    setRoot(prevRoot => updateConditionRecursively(prevRoot));
  };

  const renderRule = (rule: Rule) => {
    if ('combinator' in rule) {
      // It's a group
      return (
        <div key={rule.id} className="p-4 border rounded-lg space-y-4">
          <div className="flex items-center gap-2">
            <Select value={rule.combinator}>
              <SelectTrigger className="w-[80px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="and">AND</SelectItem>
                <SelectItem value="or">OR</SelectItem>
              </SelectContent>
            </Select>
            <Button size="sm" onClick={() => handleAddCondition(rule.id)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Rule
            </Button>
          </div>
          <div className="pl-6 space-y-4">
            {rule.rules.map(renderRule)}
          </div>
        </div>
      );
    } else {
      // It's a condition
      return (
        <div key={rule.id} className="flex items-center gap-2">
          <Select
            value={rule.fact}
            onValueChange={(value) => handleUpdateCondition(rule.id, { fact: value })}
          >
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="intent">Intent</SelectItem>
              <SelectItem value="prompt">Prompt</SelectItem>
            </SelectContent>
          </Select>
          <Select
            value={rule.operator}
            onValueChange={(value) => handleUpdateCondition(rule.id, { operator: value })}
          >
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="equals">equals</SelectItem>
              <SelectItem value="contains">contains</SelectItem>
              <SelectItem value="startsWith">starts with</SelectItem>
              <SelectItem value="endsWith">ends with</SelectItem>
            </SelectContent>
          </Select>
          <Input
            placeholder="Value"
            value={rule.value}
            onChange={(e) => handleUpdateCondition(rule.id, { value: e.target.value })}
            className="flex-1"
          />
          <Button variant="ghost" size="icon" onClick={() => handleRemoveCondition(rule.id)}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      );
    }
  };

  return (
    <div>
      {renderRule(root)}
    </div>
  );
};

export default ConditionBuilder;
