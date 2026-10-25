import { useState, useEffect } from 'react';
import QRCode from 'qrcode';
import { BACKEND_BASE_URL } from '../config/api';

interface ItemQRCodeProps {
  itemCode: string;
  serverPath?: string | null;
  className?: string;
  alt?: string;
}

export function ItemQRCode({
  itemCode,
  serverPath,
  className = "w-12 h-12 bg-white p-0.5 rounded object-contain border border-gray-200",
  alt
}: ItemQRCodeProps) {
  const [dataUrl, setDataUrl] = useState<string>('');

  useEffect(() => {
    let isCurrent = true;

    if (itemCode) {
      QRCode.toDataURL(itemCode, {
        width: 160,
        margin: 1,
        color: {
          dark: '#000000',
          light: '#ffffff'
        }
      })
        .then((url) => {
          if (isCurrent) setDataUrl(url);
        })
        .catch(() => {
          if (isCurrent && serverPath) {
            setDataUrl(`${BACKEND_BASE_URL}${serverPath}`);
          }
        });
    } else if (serverPath) {
      setDataUrl(`${BACKEND_BASE_URL}${serverPath}`);
    }

    return () => {
      isCurrent = false;
    };
  }, [itemCode, serverPath]);

  if (!dataUrl) {
    return (
      <div className={`${className} flex items-center justify-center bg-gray-800 text-[10px] text-gray-400 font-mono`}>
        QR
      </div>
    );
  }

  return (
    <img
      src={dataUrl}
      alt={alt || `QR for ${itemCode}`}
      className={className}
      loading="lazy"
    />
  );
}
