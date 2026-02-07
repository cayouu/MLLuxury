import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', loadComponent: () => import('./pages/home/home.component').then(m => m.HomeComponent) },
  { path: 'api-dotnet', loadComponent: () => import('./pages/api-dotnet/api-dotnet.component').then(m => m.ApiDotnetComponent) },
  { path: 'api-python', loadComponent: () => import('./pages/api-python/api-python.component').then(m => m.ApiPythonComponent) },
];
