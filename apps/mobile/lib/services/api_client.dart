import 'dart:convert';

import 'package:http/http.dart' as http;

/// 知行 API 网关客户端，默认指向本地开发服务。
class ApiClient {
  ApiClient({
    this.baseUrl = 'http://127.0.0.1:8080',
    http.Client? client,
  }) : _client = client ?? http.Client();

  final String baseUrl;
  final http.Client _client;

  Uri _uri(String path, [Map<String, String>? queryParameters]) {
    final normalized = path.startsWith('/') ? path : '/$path';
    return Uri.parse('$baseUrl$normalized').replace(
      queryParameters: queryParameters,
    );
  }

  Map<String, String> _headers({Map<String, String>? extra}) => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...?extra,
      };

  Future<http.Response> get(
    String path, {
    Map<String, String>? queryParameters,
    Map<String, String>? headers,
  }) {
    return _client.get(
      _uri(path, queryParameters),
      headers: _headers(extra: headers),
    );
  }

  Future<http.Response> post(
    String path, {
    Object? body,
    Map<String, String>? headers,
  }) {
    return _client.post(
      _uri(path),
      headers: _headers(extra: headers),
      body: body == null ? null : jsonEncode(body),
    );
  }

  Future<http.Response> put(
    String path, {
    Object? body,
    Map<String, String>? headers,
  }) {
    return _client.put(
      _uri(path),
      headers: _headers(extra: headers),
      body: body == null ? null : jsonEncode(body),
    );
  }

  Future<http.Response> delete(
    String path, {
    Map<String, String>? headers,
  }) {
    return _client.delete(
      _uri(path),
      headers: _headers(extra: headers),
    );
  }

  Future<Map<String, dynamic>> getJson(
    String path, {
    Map<String, String>? queryParameters,
    Map<String, String>? headers,
  }) async {
    final response = await get(
      path,
      queryParameters: queryParameters,
      headers: headers,
    );
    _throwIfError(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> postJson(
    String path, {
    Object? body,
    Map<String, String>? headers,
  }) async {
    final response = await post(path, body: body, headers: headers);
    _throwIfError(response);
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  void _throwIfError(http.Response response) {
    if (response.statusCode >= 400) {
      throw ApiException(
        statusCode: response.statusCode,
        body: response.body,
      );
    }
  }

  void close() => _client.close();
}

class ApiException implements Exception {
  const ApiException({required this.statusCode, required this.body});

  final int statusCode;
  final String body;

  @override
  String toString() => 'ApiException($statusCode): $body';
}
