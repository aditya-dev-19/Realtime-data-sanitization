import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../providers/auth_provider.dart';
import 'package:google_fonts/google_fonts.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  String _email = '';
  String _password = '';

  void _submit() {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();
      Provider.of<AuthProvider>(context, listen: false)
          .login(_email, _password)
          .then((success) {
        if (success) {
          Navigator.of(context).pushReplacementNamed('/home');
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(Provider.of<AuthProvider>(context, listen: false).error),
              backgroundColor: Colors.red,
            ),
          );
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = MediaQuery.of(context).size;
    
    return Scaffold(
      backgroundColor: const Color(0xFF121212), // Dark background
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 32.0),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header Section
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Welcome Back',
                        style: GoogleFonts.poppins(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Sign in to continue to your secure space',
                        style: GoogleFonts.poppins(
                          fontSize: 16,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 40),
                  
                  // Email Field
                  TextFormField(
                    decoration: InputDecoration(
                      labelText: 'Email',
                      labelStyle: const TextStyle(color: Colors.grey),
                      hintStyle: const TextStyle(color: Colors.grey),
                      prefixIcon: const Icon(Icons.email_outlined, color: Colors.grey),
                      filled: true,
                      fillColor: Colors.grey[900],
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Color(0xFF4A6BFF)),
                      ),
                      contentPadding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
                    ),
                    style: GoogleFonts.poppins(fontSize: 16),
                    keyboardType: TextInputType.emailAddress,
                    validator: (value) {
                      if (value == null || value.isEmpty || !value.contains('@')) {
                        return 'Please enter a valid email';
                      }
                      return null;
                    },
                    onSaved: (value) => _email = value!.trim(),
                  ),
                  
                  const SizedBox(height: 20),
                  
                  // Password Field
                  TextFormField(
                    decoration: InputDecoration(
                      labelText: 'Password',
                      labelStyle: TextStyle(color: Colors.grey[600]),
                      prefixIcon: const Icon(Icons.lock_outline, color: Colors.grey),
                      suffixIcon: IconButton(
                        icon: const Icon(Icons.visibility_outlined, color: Colors.grey),
                        onPressed: () {},
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: Colors.grey[300]!),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: Color(0xFF4A6BFF)),
                      ),
                      contentPadding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
                    ),
                    style: GoogleFonts.poppins(fontSize: 16),
                    obscureText: true,
                    validator: (value) {
                      if (value == null || value.isEmpty || value.length < 6) {
                        return 'Password must be at least 6 characters';
                      }
                      return null;
                    },
                    onSaved: (value) => _password = value!.trim(),
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // Forgot Password
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton(
                      onPressed: () {
                        // TODO: Implement forgot password
                      },
                      child: Text(
                        'Forgot Password?',
                        style: GoogleFonts.poppins(
                          color: Colors.white,
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // Login Button
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: Consumer<AuthProvider>(
                      builder: (ctx, auth, _) => auth.isLoading
                          ? const Center(child: CircularProgressIndicator())
                          : ElevatedButton(
                              onPressed: _submit,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF4A6BFF),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                elevation: 0,
                                padding: const EdgeInsets.symmetric(vertical: 16),
                              ),
                              child: Text(
                                'Sign In',
                                style: GoogleFonts.poppins(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Divider with "or"
                  Row(
                    children: [
                      Expanded(child: Divider(color: Colors.grey[300])),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0),
                        child: Text(
                          'or continue with',
                          style: GoogleFonts.poppins(
                            color: Colors.white,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      Expanded(child: Divider(color: Colors.grey[300])),
                    ],
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // Social Login Buttons
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      _buildSocialButton('assets/icons/google.svg'),
                      _buildSocialButton('assets/icons/facebook.svg'),
                      _buildSocialButton('assets/icons/apple.svg'),
                    ],
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // Don't have an account
                  Center(
                    child: GestureDetector(
                      onTap: () {
                        Navigator.of(context).pushReplacementNamed('/register');
                      },
                      child: RichText(
                        text: TextSpan(
                          text: 'Don\'t have an account? ',
                          style: GoogleFonts.poppins(
                            color: Colors.white,
                            fontSize: 14,
                          ),
                          children: [
                            TextSpan(
                              text: 'Sign Up',
                              style: GoogleFonts.poppins(
                                color: const Color(0xFF4A6BFF),
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildSocialButton(String iconPath) {
    return Container(
      width: 56,
      height: 56,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[200]!),
        borderRadius: BorderRadius.circular(12),
      ),
      child: SvgPicture.asset(
        iconPath,
        width: 24,
        height: 24,
      ),
    );
  }
}