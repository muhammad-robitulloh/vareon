import React from 'react';

interface UsageCreditBarProps {
  currentCredit: number;
  maxCredit: number;
  lowCreditThreshold: number;
}

export const UsageCreditBar: React.FC<UsageCreditBarProps> = ({
  currentCredit,
  maxCredit,
  lowCreditThreshold,
}) => {
  const percentageUsed = (currentCredit / maxCredit) * 100;
  const remainingCredit = maxCredit - currentCredit;
  const isLowCredit = currentCredit <= lowCreditThreshold;

  return (
    <div className="w-full p-4 bg-gray-800 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-300">Credit Usage</span>
        <span className="text-sm font-medium text-gray-300">
          {percentageUsed.toFixed(1)}% Used
        </span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2.5">
        <div
          className={`h-2.5 rounded-full ${isLowCredit ? 'bg-red-500' : 'bg-green-500'}`}
          style={{ width: `${percentageUsed}%` }}
        ></div>
      </div>
      <div className="flex justify-between items-center mt-2 text-sm text-gray-400">
        <span>Remaining: {remainingCredit} units</span>
        {isLowCredit && (
          <span className="text-red-400 font-semibold">Low credit! Please top up.</span>
        )}
      </div>
    </div>
  );
};
