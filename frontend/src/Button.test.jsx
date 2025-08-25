import React from 'react';
import ReactDOMServer from 'react-dom/server';
import { Button } from './components/ui/button';

it('renders button text', () => {
  const html = ReactDOMServer.renderToString(<Button>دکمه تست</Button>);
  expect(html).toContain('دکمه تست');
});
