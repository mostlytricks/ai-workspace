package com.legacy.mart.order;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class OrderController {

    private final OrderService orderService;

    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @GetMapping("/api/orders")
    public List<OrderDto> orders() {
        return orderService.listOrders();
    }

    @GetMapping("/api/customers/{id}")
    public CustomerDto customer(@PathVariable("id") long id) {
        return orderService.getCustomer(id);
    }
}
