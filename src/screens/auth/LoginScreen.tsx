import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as WebBrowser from 'expo-web-browser';
import * as AuthSession from 'expo-auth-session';
import { ENV } from '../../config/api';
import { axiosClient } from '../../api/axiosClient';
import { useAuthStore } from '../../store/authStore';

WebBrowser.maybeCompleteAuthSession();

export default function LoginScreen({ navigation }: any) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  const GOOGLE_CLIENT_ID = '600695546964-a2qcg0vtcn4o15e7pma3msimvol3n4fr.apps.googleusercontent.com';

  const handleGoogleLoginWithToken = async (idToken: string) => {
    setGoogleLoading(true);
    try {
      const res = await axiosClient.post('/auth/google-login', {
        token: idToken,
      }, {
        headers: {
          'Bypass-Tunnel-Reminder': 'true'
        }
      });

      const token = res.data.access_token;
      const userResponse = await axiosClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });

      const { signIn } = useAuthStore.getState();
      await signIn(token, userResponse.data);
    } catch (error: any) {
      const msg = error.response?.data?.detail || 'Failed to authenticate with Google';
      Alert.alert('Google Sign-In Error', msg);
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleGoogleSignInPress = async () => {
    try {
      setGoogleLoading(true);
      const callbackBase = ENV.API_BASE_URL.replace('/api/v1', '');
      const redirectUri = `${callbackBase}/api/v1/auth/google-callback`;
      const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${encodeURIComponent(GOOGLE_CLIENT_ID)}&response_type=token%20id_token&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent('openid profile email')}&nonce=${Date.now()}&prompt=select_account`;

      const result = await WebBrowser.openAuthSessionAsync(authUrl, 'jewellerapp://');

      if (result.type === 'success' && result.url) {
        const url = result.url;
        const hashIndex = url.indexOf('#');
        const queryIndex = url.indexOf('?');
        const queryString = hashIndex !== -1 ? url.substring(hashIndex + 1) : (queryIndex !== -1 ? url.substring(queryIndex + 1) : '');
        
        const params: Record<string, string> = {};
        queryString.split('&').forEach(part => {
          const [k, v] = part.split('=');
          if (k && v) params[decodeURIComponent(k)] = decodeURIComponent(v);
        });

        const token = params.token || params.id_token || params.access_token;
        if (token) {
          await handleGoogleLoginWithToken(token);
          return;
        }
      }
    } catch (e: any) {
      Alert.alert('Google Sign-In Error', e.message || 'Could not launch Google Sign-In');
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleAuth = async () => {
    const userVal = username.trim();
    const passVal = password.trim();
    const emailVal = email.trim();

    if (!userVal) {
      Alert.alert('Validation Error', 'Please enter your username');
      return;
    }
    if (isRegister && !emailVal) {
      Alert.alert('Validation Error', 'Please enter your email address');
      return;
    }
    if (!passVal) {
      Alert.alert('Validation Error', 'Please enter your password');
      return;
    }

    setLoading(true);
    try {
      if (isRegister) {
        // 1. Register new user
        await axiosClient.post('/auth/register', {
          username: userVal,
          email: emailVal,
          password: passVal
        }, {
          headers: { 'Bypass-Tunnel-Reminder': 'true' }
        });
      }

      // 2. Login with credentials
      const response = await axiosClient.post('/auth/login', {
        username: userVal,
        password: passVal
      }, {
        headers: {
          'Content-Type': 'application/json',
          'Bypass-Tunnel-Reminder': 'true'
        },
      });

      const token = response.data.access_token;
      
      // 3. Fetch user profile
      const userResponse = await axiosClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });

      // 4. Update global auth state
      const { signIn } = useAuthStore.getState();
      await signIn(token, userResponse.data);

    } catch (error: any) {
      const errorDetail = error.response?.data?.detail;
      if (errorDetail) {
        Alert.alert(isRegister ? 'Registration Failed' : 'Login Failed', errorDetail);
      } else if (error.response?.status === 401 || error.response?.status === 400) {
        Alert.alert('Login Failed', isRegister ? 'Could not create account.' : 'Incorrect username, email, or password.');
      } else {
        Alert.alert('Connection Error', 'Could not connect to the backend server. Please verify your internet connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'} 
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer} keyboardShouldPersistTaps="handled">
        <View style={styles.card}>
          {/* Header */}
          <Text style={styles.title}>SAIDEEP JEWELLERS</Text>
          <Text style={styles.subtitle}>
            {isRegister ? 'Create New Account' : 'Secure Portal Access'}
          </Text>

          {/* Username */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Username</Text>
            <TextInput
              style={styles.input}
              placeholder="e.g. admin or your username"
              placeholderTextColor="#666"
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
              autoCorrect={false}
              editable={!loading && !googleLoading}
            />
          </View>

          {/* Email (only in Register mode) */}
          {isRegister && (
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Email Address</Text>
              <TextInput
                style={styles.input}
                placeholder="you@example.com"
                placeholderTextColor="#666"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
                editable={!loading && !googleLoading}
              />
            </View>
          )}

          {/* Password */}
          <View style={styles.inputContainer}>
            <Text style={styles.label}>Password</Text>
            <TextInput
              style={styles.input}
              placeholder="••••••••"
              placeholderTextColor="#666"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              editable={!loading && !googleLoading}
            />
          </View>

          {/* Primary Action Button */}
          <TouchableOpacity 
            style={[styles.button, (loading || googleLoading) && styles.buttonDisabled]} 
            onPress={handleAuth}
            disabled={loading || googleLoading}
          >
            {loading ? (
              <ActivityIndicator color="#000" />
            ) : (
              <Text style={styles.buttonText}>
                {isRegister ? 'Sign Up' : 'Sign In'}
              </Text>
            )}
          </TouchableOpacity>

          {/* Toggle between Sign In and Sign Up */}
          <View style={styles.toggleRow}>
            <TouchableOpacity 
              onPress={() => setIsRegister(!isRegister)}
              disabled={loading || googleLoading}
            >
              <Text style={styles.toggleLink}>
                {isRegister ? 'Already have an account? Sign In' : 'Need an account? Sign Up'}
              </Text>
            </TouchableOpacity>
          </View>

          {/* Divider */}
          <View style={styles.dividerRow}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>OR</Text>
            <View style={styles.dividerLine} />
          </View>

          {/* Google Sign-In */}
          <TouchableOpacity 
            style={[styles.googleButton, (loading || googleLoading) && styles.buttonDisabled]} 
            onPress={handleGoogleSignInPress}
            disabled={loading || googleLoading}
          >
            {googleLoading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <View style={styles.googleButtonContent}>
                <Ionicons name="logo-google" size={20} color="#EA4335" style={{ marginRight: 10 }} />
                <Text style={styles.googleButtonText}>
                  {isRegister ? 'Sign up with Google' : 'Sign in with Google'}
                </Text>
              </View>
            )}
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  card: {
    backgroundColor: '#141414',
    padding: 26,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#333',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
    elevation: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#d4af37',
    textAlign: 'center',
    marginBottom: 6,
    textTransform: 'uppercase',
    letterSpacing: 1.5,
  },
  subtitle: {
    fontSize: 13,
    color: '#888',
    textAlign: 'center',
    marginBottom: 24,
  },
  inputContainer: {
    marginBottom: 16,
  },
  label: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#aaa',
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#0a0a0a',
    borderWidth: 1,
    borderColor: '#333',
    borderRadius: 8,
    padding: 13,
    color: '#fff',
    fontSize: 15,
  },
  button: {
    backgroundColor: '#d4af37',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 8,
    shadowColor: '#d4af37',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 5,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#000',
    fontSize: 15,
    fontWeight: 'bold',
  },
  toggleRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 16,
  },
  toggleLink: {
    color: '#d4af37',
    fontSize: 13,
    fontWeight: '600',
    textDecorationLine: 'underline',
  },
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 20,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#2a2a2a',
  },
  dividerText: {
    marginHorizontal: 12,
    color: '#666',
    fontSize: 12,
    fontWeight: '700',
  },
  googleButton: {
    backgroundColor: '#1f1f1f',
    borderWidth: 1,
    borderColor: '#444',
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  }
});
