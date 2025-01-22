import React, { type ReactElement } from 'react';

interface OGImageProps {
  text?: string;
}

export function OGImage({ text = '👋 Hello' }: OGImageProps): ReactElement {
  return (
    <div
      style={{
        fontSize: 40,
        color: 'black',
        background: 'white',
        width: '100%',
        height: '100%',
        padding: '50px 200px',
        textAlign: 'center',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      {text}
    </div>
  );
}
