import React from 'react';

export function IconDebug() {
  return (
    <div className="p-4 bg-yellow-100 border border-yellow-300">
      <h3 className="font-bold mb-4">ICON DEBUG TEST - Alle Ansätze:</h3>
      
      {/* Test 1: Komplett inline mit fixed dimensions */}
      <div className="mb-4">
        <h4>Test 1: Pure Inline SVG (16px fix)</h4>
        <svg
          width="16"
          height="16"
          style={{ width: '16px', height: '16px', border: '1px solid red' }}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      </div>

      {/* Test 2: Mit Tailwind Klassen */}
      <div className="mb-4">
        <h4>Test 2: Tailwind h-4 w-4</h4>
        <svg
          className="h-4 w-4"
          style={{ border: '1px solid blue' }}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      </div>

      {/* Test 3: !important Klassen */}
      <div className="mb-4">
        <h4>Test 3: !important Klassen</h4>
        <svg
          className="!h-4 !w-4"
          style={{ border: '1px solid green' }}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      </div>

      {/* Test 4: ViewBox 16x16 statt 24x24 */}
      <div className="mb-4">
        <h4>Test 4: ViewBox 16x16 (passend zur Größe)</h4>
        <svg
          width="16"
          height="16"
          style={{ width: '16px', height: '16px', border: '1px solid purple' }}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 16 16"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 2v12m6-6H2" />
        </svg>
      </div>

      {/* Test 5: Container Test */}
      <div className="mb-4">
        <h4>Test 5: In Button Container (wie im echten Code)</h4>
        <button className="inline-flex items-center p-1.5 border border-gray-300">
          <svg
            width="16"
            height="16"
            style={{ width: '16px', height: '16px', border: '1px solid orange' }}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
      </div>

      {/* Test 6: CSS Debugging */}
      <div className="mb-4">
        <h4>Test 6: Mit CSS vars</h4>
        <svg
          style={{ 
            width: 'var(--icon-size, 16px)', 
            height: 'var(--icon-size, 16px)', 
            border: '1px solid brown',
            '--icon-size': '16px'
          } as React.CSSProperties}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      </div>
    </div>
  );
}

export default IconDebug;