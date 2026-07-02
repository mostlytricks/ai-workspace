package com.legacy.mart.inventory;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class InventoryController {

    private final Map<String, Integer> stockCache = new ConcurrentHashMap<>();

    @GetMapping("/api/stock")
    public Map<String, Object> stock(@RequestParam("sku") String sku) {
        int qty = stockCache.getOrDefault(sku, 0);
        return Map.of("sku", sku, "qty", qty);
    }
}
