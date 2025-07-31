import type { SVGProps } from 'react';

// Icon paths - zentraler Ort für alle SVG-Pfade
const iconPaths = {
  // Documents & Files
  document: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  folder: 'M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z',
  
  // Actions
  plus: 'M12 4v16m8-8H4',
  trash: 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16',
  edit: 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 013.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z',
  refresh: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15',
  
  // Status
  check: 'M5 13l4 4L19 7',
  x: 'M6 18L18 6M6 6l12 12',
  checkCircle: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  xCircle: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z',
  
  // Navigation
  chevronRight: 'M9 5l7 7-7 7',
  chevronDown: 'M19 9l-7 7-7-7',
  search: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z',
  
  // Info & Warning
  info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  warning: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z',
  
  // Misc
  external: 'M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14'
};

// Größen-Mapping - zentrale Verwaltung aller Icon-Größen
// WICHTIG: Sowohl className als auch width/height sind erforderlich!
const sizeMap = {
  xs: { className: 'h-3 w-3 flex-shrink-0', width: 12, height: 12 },
  sm: { className: 'h-4 w-4 flex-shrink-0', width: 16, height: 16 },
  md: { className: 'h-5 w-5 flex-shrink-0', width: 20, height: 20 },
  lg: { className: 'h-6 w-6 flex-shrink-0', width: 24, height: 24 },
  xl: { className: 'h-8 w-8 flex-shrink-0', width: 32, height: 32 }
};

// Color presets für häufig verwendete Farben
const colorMap = {
  gray: 'text-gray-400 dark:text-gray-500',
  blue: 'text-blue-600 dark:text-blue-400',
  green: 'text-green-600 dark:text-green-400',
  red: 'text-red-600 dark:text-red-400',
  yellow: 'text-yellow-600 dark:text-yellow-400',
  white: 'text-white',
  current: '' // Verwendet aktuelle Textfarbe
};

export interface IconProps {
  name: keyof typeof iconPaths;
  size?: keyof typeof sizeMap;
  color?: keyof typeof colorMap | string;
  className?: string;
  animate?: 'spin' | 'bounce' | 'pulse';
  onClick?: () => void;
  title?: string;
}

export function Icon({
  name,
  size = 'sm',
  color = 'gray',
  className = '',
  animate,
  onClick,
  title
}: IconProps) {
  const sizeConfig = sizeMap[size];
  const colorClass = colorMap[color as keyof typeof colorMap] || color;
  
  const animationClass = animate ? `animate-${animate}` : '';
  
  const combinedClassName = [
    sizeConfig.className,
    colorClass,
    animationClass,
    onClick ? 'cursor-pointer' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <svg
      className={combinedClassName}
      width={sizeConfig.width}
      height={sizeConfig.height}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
      onClick={onClick}
    >
      {title && <title>{title}</title>}
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d={iconPaths[name]}
      />
    </svg>
  );
}

export default Icon;