import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:in_app_purchase/in_app_purchase.dart';
import '../services/iap_service.dart';

class SubscriptionScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final iapService = Provider.of<IAPService>(context);

    return Scaffold(
      appBar: AppBar(title: Text("Upgrade to Pro")),
      body: iapService.isAvailable
          ? ListView(
              children: iapService.products.map((ProductDetails product) {
                return Card(
                  child: ListTile(
                    title: Text(product.title),
                    subtitle: Text(product.description),
                    trailing: Text(product.price),
                    onTap: () {
                      iapService.buyProduct(product);
                    },
                  ),
                );
              }).toList(),
            )
          : Center(child: Text("Store not available")),
    );
  }
}
