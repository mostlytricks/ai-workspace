package com.legacy.mart.order;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface OrderMapper {

    List<OrderDto> selectOrders();

    CustomerDto selectCustomerById(long id);
}
