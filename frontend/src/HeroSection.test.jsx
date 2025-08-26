import React from 'react';
import ReactDOMServer from 'react-dom/server';
import { HeroSection } from './App';

it('renders hero text', () => {
  const html = ReactDOMServer.renderToString(<HeroSection onProductsClick={() => {}} />);
  expect(html).toContain('برای پزشکان');
  expect(html).toContain('و متخصصان پزشکی');
});
