import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in Leaflet with React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface MapPoint {
  id: number;
  name: string;
  lat: number;
  lng: number;
  description?: string;
}

interface MapProps {
  points?: MapPoint[];
  center?: [number, number];
  zoom?: number;
  height?: string;
  className?: string;
  onPointClick?: (point: MapPoint) => void;
  showControls?: boolean;
}

export default function Map({ 
  points = [], 
  center = [55.7558, 37.6173], // Moscow by default
  zoom = 13,
  height = '300px',
  className = '',
  onPointClick,
  showControls = true
}: MapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<L.Marker[]>([]);

  useEffect(() => {
    if (!mapRef.current) return;

    // Initialize map
    const map = L.map(mapRef.current).setView(center, zoom);
    mapInstanceRef.current = map;

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Add controls if enabled
    if (showControls) {
      L.control.scale().addTo(map);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [center, zoom, showControls]);

  useEffect(() => {
    if (!mapInstanceRef.current) return;

    // Clear existing markers
    markersRef.current.forEach(marker => {
      mapInstanceRef.current?.removeLayer(marker);
    });
    markersRef.current = [];

    // Add new markers
    points.forEach(point => {
      const marker = L.marker([point.lat, point.lng])
        .addTo(mapInstanceRef.current!)
        .bindPopup(`
          <div class="p-2">
            <h3 class="font-semibold text-sm">${point.name}</h3>
            ${point.description ? `<p class="text-xs text-gray-600 mt-1">${point.description}</p>` : ''}
          </div>
        `);

      if (onPointClick) {
        marker.on('click', () => onPointClick(point));
      }

      markersRef.current.push(marker);
    });

    // Fit map to show all points if there are any
    if (points.length > 0) {
      const group =  L.featureGroup(markersRef.current);
      mapInstanceRef.current.fitBounds(group.getBounds().pad(0.1));
    }
  }, [points, onPointClick]);

  return (
    <div 
      ref={mapRef} 
      className={`rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 ${className}`}
      style={{ height }}
    />
  );
}

// Mini map component for posts
export function MiniMap({ 
  points = [], 
  className = '' 
}: { 
  points?: MapPoint[];
  className?: string;
}) {
  return (
    <Map 
      points={points}
      height="200px"
      zoom={15}
      showControls={false}
      className={className}
    />
  );
}

// Full screen map modal
export function MapModal({ 
  points, 
  isOpen, 
  onClose, 
  title = "Карта" 
}: { 
  points: MapPoint[];
  isOpen: boolean;
  onClose: () => void;
  title?: string;
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose}></div>
      <div className="relative bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-6xl h-[90vh] flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">{title}</h3>
          <button 
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <svg className="w-5 h-5 text-gray-700 dark:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="flex-1">
          <Map 
            points={points}
            height="100%"
            zoom={points.length === 1 ? 15 : 10}
            showControls={true}
          />
        </div>
      </div>
    </div>
  );
}


