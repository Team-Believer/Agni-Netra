'use client';

import LiveMapPage from '../page';

export default function ParameterizedLiveMapPage({ params }: { params: { eventId: string } }) {
  return <LiveMapPage params={params} />;
}
