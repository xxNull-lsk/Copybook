import 'package:flutter/material.dart';

class NumChangeWidget extends StatefulWidget {
  final double height;
  final int num;
  final int min;
  final int max;
  final ValueChanged<int> onValueChanged;

  const NumChangeWidget(
      {required this.onValueChanged,
      super.key,
      this.height = 36.0,
      this.num = 0,
      this.min = 0,
      this.max = -1});

  @override
  State<NumChangeWidget> createState() => _NumChangeWidgetState();
}

class _NumChangeWidgetState extends State<NumChangeWidget> {
  int num = 0;
  @override
  void initState() {
    super.initState();

    num = widget.num;
  }

  @override
  Widget build(BuildContext context) {
    num = widget.num;
    return Container(
      height: widget.height,
      decoration: BoxDecoration(
        borderRadius: const BorderRadius.all(Radius.circular(2.0)),
        border: Border.all(color: Colors.grey, width: 0.5),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          GestureDetector(
            onTap: _minusNum,
            child: Container(
              width: 32.0,
              alignment: Alignment.center,
              child: const Icon(Icons.minimize),
            ),
          ),
          Container(
            width: 0.5,
            color: Colors.grey,
          ),
          Container(
            width: 62.0,
            alignment: Alignment.center,
            child: Text(
              num.toString(),
              maxLines: 1,
              style: const TextStyle(fontSize: 20.0, color: Colors.black),
            ),
          ),
          Container(
            width: 0.5,
            color: Colors.grey,
          ),
          GestureDetector(
            onTap: _addNum,
            child: Container(
              width: 32.0,
              alignment: Alignment.center,
              child: const Icon(Icons.add),
            ),
          ),
        ],
      ),
    );
  }

  void _minusNum() {
    if (num <= widget.min) {
      return;
    }

    setState(() {
      num -= 1;
      widget.onValueChanged(num);
    });
  }

  void _addNum() {
    if (num >= widget.max) {
      return;
    }

    setState(() {
      num += 1;
      widget.onValueChanged(num);
    });
  }
}
