from canteenWS import bp

@bp.route('/canteens/<int:id>', methods=['GET'])
def get_user(id):
    pass

@bp.route('/canteens', methods=['GET'])
def get_users():
    pass

@bp.route('/canteens/<int:id>/followers', methods=['GET'])
def get_followers(id):
    pass

@bp.route('/canteens/<int:id>/followed', methods=['GET'])
def get_followed(id):
    pass

@bp.route('/canteens', methods=['POST'])
def create_user():
    pass

@bp.route('/canteens/<int:id>', methods=['PUT'])
def update_user(id):
    pass