import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:in_app_purchase/in_app_purchase.dart';

class ApiService {
  // Replace with your actual backend URL (e.g. 10.0.2.2 for Android emulator)
  static const String _baseUrl = "http://10.0.2.2:8000"; // Android Emulator localhost
  String? _authToken;

  void setAuthToken(String token) {
    _authToken = token;
  }

  Future<bool> verifyPurchase(PurchaseDetails purchase) async {
    final verificationData = purchase.verificationData;
    
    try {
      final response = await http.post(
        Uri.parse("$_baseUrl/purchases/verify"),
        headers: {
          "Content-Type": "application/json",
          if (_authToken != null) "Authorization": "Bearer $_authToken",
        },
        body: jsonEncode({
          'source': verificationData.source,
          'verificationData': verificationData.serverVerificationData, // Purchase Token
          'productId': purchase.productID,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['status'] == 'valid';
      }
    } catch (e) {
      print('Error verifying purchase: $e');
    }
    return false;
  }
  Future<void> syncUser(String token) async {
    _authToken = token; // Cache internally
    try {
      final response = await http.post(
        Uri.parse("$_baseUrl/auth/login"),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $token",
        },
      );
      if (response.statusCode == 200) {
        print("User synced: ${response.body}");
      } else {
        print("User sync failed: ${response.statusCode}");
      }
    } catch (e) {
      print("Error syncing user: $e");
    }
  }
}
