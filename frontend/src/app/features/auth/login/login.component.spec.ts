import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { LoginComponent } from './login.component';

describe('LoginComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginComponent],
      providers: [
        provideRouter([]),
        provideHttpClient()
      ]
    }).compileComponents();
  });

  it('should create the login component', () => {
    const fixture = TestBed.createComponent(LoginComponent);
    const component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });

  it('should initialize an invalid form with required fields', () => {
    const fixture = TestBed.createComponent(LoginComponent);
    fixture.detectChanges();
    const component = fixture.componentInstance;
    expect(component.loginForm.valid).toBe(false);
    expect(component.loginForm.get('login')?.valid).toBe(false);
    expect(component.loginForm.get('motDePasse')?.valid).toBe(false);
  });

  it('should be valid when valid credentials are provided', () => {
    const fixture = TestBed.createComponent(LoginComponent);
    fixture.detectChanges();
    const component = fixture.componentInstance;

    component.loginForm.setValue({
      login: 'ibrahima_sow',
      motDePasse: 'SecretPass123!'
    });

    expect(component.loginForm.valid).toBe(true);
  });
});
