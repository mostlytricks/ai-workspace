package com.legacy.mart.order;

import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class OrderService {

    private final OrderMapper orderMapper;
    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${inventory.base-url}")
    private String inventoryBaseUrl;

    public OrderService(OrderMapper orderMapper) {
        this.orderMapper = orderMapper;
    }

    public List<OrderDto> listOrders() {
        List<OrderDto> orders = orderMapper.selectOrders();
        for (OrderDto o : orders) {
            StockDto stock = restTemplate.getForObject(
                    inventoryBaseUrl + "/api/stock?sku=" + o.getSku(), StockDto.class);
            o.setInStock(stock != null && stock.getQty() > 0);
        }
        return orders;
    }

    public CustomerDto getCustomer(long id) {
        return orderMapper.selectCustomerById(id);
    }
}
