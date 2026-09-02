import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [RouterOutlet],
  template: '<main class="admin-layout"><router-outlet></router-outlet></main>'
})
export class AdminLayoutComponent {}
